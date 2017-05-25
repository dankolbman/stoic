import time
import json
import jwt
from datetime import datetime
from flask import current_app, url_for

from geo import create_app, db
from geo.model import Point, Line

from utils import FlaskTestCase


class InterpTestCase(FlaskTestCase):

    def test_status(self):
        """ Check that the api status is returning 200 """
        response = self.client.get(url_for('points_status'))
        # Check response
        self.assertTrue(response.status_code == 200)
        # Check content of json response status
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['status'] == 200)
        self.assertTrue(json_response['version'] == '1.0')

    def test_interpolation(self):
        """ test interpolating of points """
        # test upload valid file
        data = dict(file=(open('test/data/test_points.csv', 'rb'),
                          "test_points.csv"))
        response = self.client.post(
                    url_for('points_points_csv', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    content_type='multipart/form-data',
                    data=data),
        json_response = json.loads(response[0].data.decode('utf-8'))

        response = self.client.get(
                    url_for('interp_interp', username='Dan', trip='trip1'),
                    query_string={'time': '2017-04-29T05:01:39'},
                    headers=self._api_headers())
        json_response = json.loads(response.data.decode('utf-8'))
        point = json_response['point']
        self.assertLess(point['geometry']['coordinates'][0], -82.62)
        self.assertGreater(point['geometry']['coordinates'][1], 42.865)

        response = self.client.get(
                    url_for('interp_interp', username='Dan', trip='trip1'),
                    query_string={'time': '2017-04-23T05:01:39'},
                    headers=self._api_headers())
        json_response = json.loads(response.data.decode('utf-8'))
        point = json_response['point']
        self.assertAlmostEqual(point['geometry']['coordinates'][0], -82.62, 1)
        self.assertAlmostEqual(point['geometry']['coordinates'][1], 42.865, 1)

        response = self.client.get(
                    url_for('interp_interp', username='Dan', trip='trip1'),
                    query_string={'time': '2017-05-23T05:01:39'},
                    headers=self._api_headers())
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 400)
