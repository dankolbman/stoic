import json
from dateutil import parser
from flask import current_app, url_for
from geo import create_app, db

from geo.model import Point
from geo.tasks.csv import parse_csv

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
        self.assertTrue(all([int(p[0]) == 42 for p in coords]))
        self.assertTrue(all([int(p[1]) == -82 for p in coords]))
        dts = [parser.parse(p['properties']['created_at'])
               for p in json_response['points']]
        self.assertTrue(all([dt.year == 2017 and dt.month == 4 for dt in dts]))
