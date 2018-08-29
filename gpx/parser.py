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
    def haversine_distance(point1, point2):
        # https://www.movable-type.co.uk/scripts/latlong.html
        latitude_1 = point1['lat']
        latitude_2 = point2['lat']
        longitude_1 = point1['lon']
        longitude_2 = point2['lon']

        delta_latitude = math.radians(latitude_2 - latitude_1)
        delta_longitude = math.radians(longitude_2 - longitude_1)

        a = math.sin(delta_latitude / 2) * math.sin(delta_latitude / 2) + \
            math.cos(math.radians(latitude_1)) * math.cos(math.radians(longitude_2)) * \
            math.sin(delta_longitude / 2) * math.sin(delta_longitude / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return 6371e3 * c

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

    def __smoothed_speeds(self):
        pass

    def get_moving_data(self):
        size = len(self.points)

        distance = 0.
        moving_time = 0.
        max_speed = 0.

        for n, point in enumerate(self.points):
            if n < size - 2:
                distance += self.haversine_distance(point, self.points[n + 1])

        return distance, moving_time, max_speed
