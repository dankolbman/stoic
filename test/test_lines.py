import time
import json
import jwt
from random import random
from datetime import datetime, timedelta
from flask import current_app, url_for

from geo import create_app, db
from geo.model import Point, Line
from geo.tasks.csv import parse_csv
from geo.tasks.lines import line_from_points

from utils import FlaskTestCase


class LinesTestCase(FlaskTestCase):

    def _generate_points(self, n=10, trip='trip'):
        now = datetime.utcnow()
        pts = []
        for i in range(n):
            now = now + timedelta(seconds=75)
            pts.append({"type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [random()*90.0,
                                            random()*360.0-180.0],
                            },
                        "properties": {
                            "username": "Dan",
                            "trip_id": trip,
                            "created_at": now.isoformat(),
                            "accuracy": 25.0
                            }
                        })
        return {"points": pts}

    def test_status(self):
        """ Check that the api status is returning 200 """
        response = self.client.get(url_for('lines_status'))
        # Check response
        self.assertTrue(response.status_code == 200)
        # Check content of json response status
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['status'] == 200)
        self.assertTrue(json_response['version'] == '1.0')

        response = self.client.get(url_for('status'))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['status'] == 200)
        self.assertEqual(len(json_response['version']), 7)

    def test_lines(self):
        """ Test lines endpoint """
        response = self.client.get(
                    url_for('lines_lines', username='Dan', trip='trip1'),
                    headers=self._api_headers())
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['lines']), 0)
        self.assertEqual(json_response['count'], 0)
        # add a bunch of points
        pt_json = self._generate_points(21, trip='trip1')
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        line_from_points(('Dan', 'trip1'))
        self.assertEqual(Line.objects.count(), 1)
        t = datetime.utcnow().isoformat()
        # test general line properties
        response = self.client.get(
                    url_for('lines_lines', username='Dan', trip='trip1'),
                    headers=self._api_headers())
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['count'], 1)
        line = json_response['lines'][0]
        self.assertEqual(len(line['geometry']['coordinates']), 21)
