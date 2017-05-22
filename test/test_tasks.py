import json
from dateutil import parser
from flask import current_app, url_for
from geo import create_app, db

from geo.model import Point, Line
from geo.tasks.csv import parse_csv
from geo.tasks.lines import line_from_points

from utils import FlaskTestCase


class TaskTestCase(FlaskTestCase):

    def test_parse_csv(self):
        """
        test that csv is parsed and points are inserted to database
        """
        parse_csv('test/data/test_points.csv', 'Dan', 'trip1')
        self.assertEqual(Point.objects.count(), 9)
        response = self.client.get(
                    url_for('points_points', username='Dan', trip='trip1'),
                    headers=self._api_headers())
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['count'], 9)

        coords = [p['geometry']['coordinates']
                  for p in json_response['points']]
        self.assertTrue(all([int(p[0]) == -82 for p in coords]))
        self.assertTrue(all([int(p[1]) == 42 for p in coords]))
        self.assertTrue(all([len(p) == 2 for p in coords]))
        dts = [parser.parse(p['properties']['created_at'])
               for p in json_response['points']]
        self.assertTrue(all([dt.year == 2017 and dt.month == 4 for dt in dts]))

    def test_line_from_points(self):
        """
        test that a line is properly created from a set of points
        """
        chain = (parse_csv.s('test/data/test_points.csv', 'Dan', 'trip1') |
                 line_from_points.s())
        chain()

        self.assertEqual(Point.objects.count(), 9)
        self.assertEqual(Line.objects.count(), 1)
        line = Line.objects.limit(1)[0]
        self.assertEqual(len(line.coords), 4)
        line_json = line.to_json()
        geom = line_json['geometry']
        self.assertEqual(geom['type'], 'LineString')
        props = line_json['properties']
        self.assertEqual(props['username'], 'Dan')
        self.assertEqual(props['trip_id'], 'trip1')
        self.assertIn('2017-04-29T05:00:16', props['start_at'])
        self.assertIn('2017-04-29T05:08:04', props['end_at'])
