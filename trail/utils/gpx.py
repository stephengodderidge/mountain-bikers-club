import io
import math
import xml.etree.ElementTree as ET
import re
import urllib.request
import urllib.parse

from dateutil.parser import parse as parse_time
from staticmap import StaticMap, Line


def cheap_ruler_distance(points):
    # https://github.com/mapbox/cheap-ruler
    cos = math.cos(points[0]['lat'] * math.pi / 180)
    cos2 = 2 * cos * cos - 1
    cos3 = 2 * cos * cos2 - cos
    cos4 = 2 * cos * cos3 - cos2
    cos5 = 2 * cos * cos4 - cos3

    kx = 1000 * (111.41513 * cos - 0.09455 * cos3 + 0.00012 * cos5)
    ky = 1000 * (111.13209 - 0.56605 * cos2 + 0.0012 * cos4)

    size = len(points)
    distance = 0.0

    for n, point in enumerate(points):
        if n < size - 1:
            dx = (points[n]['lon'] - points[n+1]['lon']) * kx
            dy = (points[n]['lat'] - points[n+1]['lat']) * ky

            distance += math.sqrt(dx * dx + dy * dy)

    return distance


def get_location(point):
    url = 'https://nominatim.openstreetmap.org/reverse?lon=' + str(point['lon']) + '&lat=' + str(point['lat'])
    headers = {'User-Agent': 'mountainbikers.club'}
    req = urllib.request.Request(url, headers=headers)
    location = None

    # FIXME Manage errors
    with urllib.request.urlopen(req) as response:
        reverse_xml = response.read()
        reverse_root = ET.fromstring(reverse_xml)

        if reverse_root is not None and reverse_root.tag == 'reversegeocode':
            location = reverse_root.find('addressparts/village')
            if location is None:
                location = reverse_root.find('addressparts/town')

    return location.text if location is not None else None


def get_smoothed_data(points, key=None, fn=lambda p, c, n: p * .3 + c * .4 + n * .3):
    size = len(points)

    def __filter(n):
        current_data = points[n][key] if key else points[n]

        if current_data is None:
            return False

        if 0 < n < size - 1:
            previous_data = points[n - 1][key] if key else points[n - 1]
            next_data = points[n + 1][key] if key else points[n + 1]

            if previous_data is not None and current_data is not None and next_data is not None:
                return fn(previous_data, current_data, next_data)

        return current_data

    return list(map(__filter, range(size)))


def get_smoothed_speed(points):
    size = len(points)

    def __filter(n):
        current_time = points[n]['time']

        if current_time is None:
            return False

        current_time = parse_time(points[n]['time'])

        if 0 < n < size - 1:
            previous_time = parse_time(points[n - 1]['time'])
            next_time = parse_time(points[n + 1]['time'])

            if previous_time is not None and current_time is not None and next_time is not None:
                delta_time = previous_time - next_time
                delta_time = math.fabs(delta_time.total_seconds())

                distance1 = cheap_ruler_distance([points[n - 1], points[n]])
                distance2 = cheap_ruler_distance([points[n], points[n + 1]])
                distance = distance1 + distance2

                speed = distance / delta_time

                return speed

        return 0.

    return get_smoothed_data(list(map(__filter, range(size))))


def get_uphill_downhill(elevations):
    uphill = 0.0
    downhill = 0.0

    for n, elevation in enumerate(elevations):
        if n > 0:
            d = elevation - elevations[n - 1]
            if d > 0:
                uphill += d
            else:
                downhill -= d

    return uphill, downhill


def parse(xml):
    # Remove namespace to ease nodes selection
    gpx_xml = re.sub(' xmlns="[^"]+"', '', xml, count=1)
    root = ET.fromstring(gpx_xml)

    if root.tag != 'gpx' and root.attrib['version'] != '1.1':
        print('Not a GPX 1.1')

    name = root.find('metadata/name') or root.find('trk/name')
    description = root.find('metadata/desc') or root.find('trk/desc')

    parsed_tracks = []
    tracks = root.findall('trk')
    for track in tracks:
        parsed_points = []
        segments = track.findall('trkseg')
        for segment in segments:
            points = segment.findall('trkpt')
            for point in points:
                elevation = point.find('ele')
                time = point.find('time')

                # TODO parse extensions
                current_point = {
                    'lat': float(point.attrib['lat']),
                    'lon': float(point.attrib['lon']),
                    'ele': float(elevation.text) if elevation is not None else None,
                    'time': time.text if time is not None else None,
                }

                parsed_points.append(current_point)

        smoothed_speeds = get_smoothed_speed(parsed_points)
        smoothed_elevations = get_smoothed_data(parsed_points, 'ele')
        uphill, downhill = get_uphill_downhill(smoothed_elevations)

        track_name = track.find('name')
        track_description = track.find('desc')

        # TODO: Moving time?
        parsed_tracks.append({
            'name': track_name.text if track_name else None,
            'description': track_description.text if track_description else None,
            'location': get_location(parsed_points[0]),
            'distance': cheap_ruler_distance(parsed_points),
            'uphill': uphill,
            'downhill': downhill,
            'points': parsed_points,
            'smoothed_elevations': smoothed_elevations,
            'smoothed_speeds': smoothed_speeds,
        })

    return name, description, parsed_tracks


def get_coordinates(points):
    return list(map(lambda p: (p['lon'], p['lat']), points))


def get_track_image(points, width, height):
    coordinates = get_coordinates(points)
    m = StaticMap(int(width), int(height), 10, 10, 'https://b.tile.opentopomap.org/{z}/{x}/{y}.png')
    m.add_line(Line(coordinates, 'white', 11))
    m.add_line(Line(coordinates, '#2E73B8', 5))
    image = m.render()
    f = io.BytesIO(b'')
    image.save(f, format='JPEG', optimize=True, progressive=True)

    return f


def get_track_details(track):
    start_datetime = track['points'][0]['time']
    end_datetime = track['points'][-1]['time']

    total_time = None
    average_speed = None

    if start_datetime and end_datetime:
        start_datetime = parse_time(start_datetime)
        end_datetime = parse_time(end_datetime)
        total_time = math.fabs((end_datetime - start_datetime).total_seconds())
        average_speed = (track['distance'] / total_time) * 3600. / 1000.

    return {
        'name': track['name'],
        'description': track['description'],
        'location': track['location'],
        'distance': track['distance'] / 1000.,
        'uphill': track['uphill'],
        'downhill': track['downhill'],
        'start_datetime': start_datetime,
        'end_datetime': end_datetime,
        'min_altitude': min(track['smoothed_elevations']),
        'max_altitude': max(track['smoothed_elevations']),
        'max_speed': max(track['smoothed_speeds']) * 3600. / 1000.,
        'total_time': total_time,
        'average_speed': average_speed,
    }
