import time
import json
import jwt
from random import random
from datetime import datetime
from flask import current_app, url_for

from geo import create_app, db
from geo.model import Point

from utils import FlaskTestCase


class LinesTestCase(FlaskTestCase):

    def _generate_points(self, n=10, trip='trip'):
        pts = []
        for i in range(n):
            time.sleep(0.001)
            pts.append({"type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [random()*90.0,
                                            random()*360.0-180.0],
                            },
                        "properties": {
                            "username": "Dan",
                            "trip_id": trip,
                            "created_at": datetime.utcnow().isoformat(),
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

    def test_lines(self):
        """ Test lines endpoint """
        # add a bunch of points
        pt_json = self._generate_points(21, trip='trip1')
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        t = datetime.utcnow().isoformat()
        # post a second batch of points to get different timestamps
        pt_json = self._generate_points(5, trip='trip1')
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        # test general line properties
        response = self.client.get(
                    url_for('lines_lines', username='Dan', trip='trip1'),
                    headers=self._api_headers())
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['lines']), 1)
        line = json_response['lines'][0]
        self.assertEqual(len(line['geometry']['coordinates']), 26)
        self.assertTrue(line['properties']['start_at'] <
                        line['properties']['end_at'])
        # test the start param
        response = self.client.get(
                    url_for('lines_lines', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    query_string=dict(start=t))
        json_response = json.loads(response.data.decode('utf-8'))
        line = json_response['lines'][0]
        self.assertEqual(len(line['geometry']['coordinates']), 5)
        # test the size param
        response = self.client.get(
                    url_for('lines_lines', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    query_string=dict(size=7))
        json_response = json.loads(response.data.decode('utf-8'))
        line = json_response['lines'][0]
        self.assertEqual(len(line['geometry']['coordinates']), 7)
