import math
import xml.etree.ElementTree as ET
import re
import urllib.request
import urllib.parse

from dateutil.parser import parse as parse_time


class GPXParser:
    def __init__(self, xml):

        # Remove namespace to ease nodes selection
        gpx_xml = re.sub(' xmlns="[^"]+"', '', xml, count=1)
        root = ET.fromstring(gpx_xml)

        if root.tag != 'gpx' and root.attrib['version'] != '1.1':
            print('Not a GPX 1.1')

        self.root = root
        self.points = self.__parse()

    @staticmethod
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

    def __parse(self):
        all_points = []
        tracks = self.root.findall('trk')
        # FIXME Split tracks
        for track in tracks:
            segments = track.findall('trkseg')
            for segment in segments:
                points = segment.findall('trkpt')
                for point in points:
                    elevation = point.find('ele')
                    time = point.find('time')

                    current_point = {
                        'lat': float(point.attrib['lat']),
                        'lon': float(point.attrib['lon']),
                        'ele': float(elevation.text) if elevation is not None else None,
                        'time': parse_time(time.text) if time is not None else None,
                    }

                    all_points.append(current_point)

        return all_points

    def get_metadata(self):
        size = len(self.points)

        name = self.root.find('metadata/name') or self.root.find('trk/name')
        description = self.root.find('metadata/desc') or self.root.find('trk/desc')
        location = None

        if name is not None:
            name = name.text

        if description is not None:
            description = description.text

        start_time = self.points[0]['time']
        end_time = self.points[size - 1]['time']

        url = 'https://nominatim.openstreetmap.org/reverse?lat=' + str(self.points[0]['lat']) + '&lon=' + str(self.points[0]['lon'])
        headers = {'User-Agent': 'mountainbikers.club'}
        req = urllib.request.Request(url, headers=headers)

        # FIXME Manage errors
        with urllib.request.urlopen(req) as response:
            reverse_xml = response.read()
            reverse_root = ET.fromstring(reverse_xml)

            if reverse_root is not None and reverse_root.tag == 'reversegeocode':
                location = reverse_root.find('addressparts/village')
                if location is None:
                    location = reverse_root.find('addressparts/town')

        location = location.text if location is not None else None

        return name, description, start_time, end_time, location

    def __smoothed_elevations(self):
        size = len(self.points)

        def __filter(n):
            current_elevation = self.points[n]['ele']

            if current_elevation is None:
                return False

            if 0 < n < size - 1:
                previous_elevation = self.points[n - 1]['ele']
                next_elevation = self.points[n + 1]['ele']

                if previous_elevation is not None and current_elevation is not None and next_elevation is not None:
                    return previous_elevation * .3 + current_elevation * .4 + next_elevation * .3

            return current_elevation

        return list(map(__filter, range(size)))

    def __smoothed_speeds(self):
        size = len(self.points)

        def __filter(n):
            current_time = self.points[n]['time']

            if current_time is None:
                return False

            if 0 < n < size - 1:
                previous_time = self.points[n - 1]['time']
                next_time = self.points[n + 1]['time']

                if previous_time is not None and current_time is not None and next_time is not None:
                    delta_time = previous_time - next_time
                    delta_time = math.fabs(delta_time.total_seconds())

                    distance1 = self.cheap_ruler_distance([self.points[n - 1], self.points[n]])
                    distance2 = self.cheap_ruler_distance([self.points[n], self.points[n + 1]])
                    distance = distance1 + distance2

                    speed = distance / delta_time

                    return speed

            return 0.

        speed = list(map(__filter, range(size)))

        # FIXME merge this with __smoothed_elevation as static __smoother
        def __filter2(n):
            current_speed = speed[n]

            if current_speed is None:
                return False

            if 0 < n < size - 1:
                previous_speed = speed[n - 1]
                next_speed = speed[n + 1]

                if previous_speed is not None and current_speed is not None and next_speed is not None:
                    return previous_speed * .3 + current_speed * .4 + next_speed * .3

            return current_speed

        smoothed_speeds = list(map(__filter2, range(size)))

        return smoothed_speeds

    def get_elevation_data(self):
        smoothed_elevations = self.__smoothed_elevations()
        min_elevation = smoothed_elevations[0]
        max_elevation = smoothed_elevations[0]
        uphill = 0.0
        downhill = 0.0

        for n, elevation in enumerate(smoothed_elevations):
            if elevation < min_elevation:
                min_elevation = elevation
            if elevation > max_elevation:
                max_elevation = elevation
            if n > 0:
                d = elevation - smoothed_elevations[n - 1]
                if d > 0:
                    uphill += d
                else:
                    downhill -= d

        return min_elevation, max_elevation, uphill, downhill

    def get_moving_data(self):
        smoothed_speeds = self.__smoothed_speeds()
        moving_time = 0.
        max_speed = max(smoothed_speeds)
        distance = self.cheap_ruler_distance(self.points)

        return distance, moving_time, max_speed
