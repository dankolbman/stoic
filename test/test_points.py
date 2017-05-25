import time
import json
import jwt
from random import random
from datetime import datetime
from flask import current_app, url_for

from geo import create_app, db
from geo.model import Point, Line

from utils import FlaskTestCase


class PointsTestCase(FlaskTestCase):

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
        response = self.client.get(url_for('points_status'))
        # Check response
        self.assertTrue(response.status_code == 200)
        # Check content of json response status
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['status'] == 200)
        self.assertTrue(json_response['version'] == '1.0')

    def test_points(self):
        """ Test points endpoint """
        self.assertEqual(Point.objects.count(), 0)
        point = Point(lon=-87.682321,
                      lat=41.839344,
                      username='Dan',
                      accuracy=10.0,
                      trip_id='default')
        point.save()
        self.assertEqual(Point.objects.count(), 1)

        response = self.client.get(url_for('points_points',
                                           username='Dan',
                                           trip='default'))
        # check response
        self.assertEqual(response.status_code, 200)
        # check content of json response status
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['count'], 1)
        self.assertEqual(json_response['count'], len(json_response['points']))

    def test_no_points(self):
        """ Test response for empty post """
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='default'),
                    headers=self._api_headers(),
                    data=json.dumps({}))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(json_response['message'], 'no points created')
        self.assertEqual(json_response['status'], 200)

    def test_missing_points(self):
        """ Test response for empty post """
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='default'),
                    headers=self._api_headers(),
                    data=json.dumps({'points': []}))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertIn('missing', json_response['message'])
        self.assertEqual(json_response['status'], 400)

    def test_no_auth(self):
        """ Test response for no JWT token """
        headers = self._api_headers()
        del headers['Authorization']
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='default'),
                    headers=headers,
                    data=json.dumps({'points': []}))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status, '403 FORBIDDEN')
        self.assertEqual(json_response['status'], 403)

    def test_wrong_user(self):
        """ Test that one user cannot post to another user's points"""
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='default'),
                    headers=self._api_headers('Steve'),
                    data=json.dumps({'points': []}))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status, '403 FORBIDDEN')
        self.assertEqual(json_response['status'], 403)

    def test_pagination(self):
        """ Test pagination of points """
        # add a bunch of points
        pt_json = self._generate_points(13, trip='trip1')
        # post points through api
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
        # get the points
        response = self.client.get(
                    url_for('points_points', username='Dan', trip='trip1'),
                    headers=self._api_headers())
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['points']), 10)
        self.assertEqual(json_response['count'], 18)
        # test size param
        response = self.client.get(
                    url_for('points_points', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    query_string=dict(size=15))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['points']), 15)
        # test the start param
        response = self.client.get(
                    url_for('points_points', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    query_string=dict(start=t, size=10))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['points']), 5)

    def test_single_point_submission(self):
        """ test submission of single point """
        pt_json = self._generate_points(1, trip='testing')

        response = self.client.post(
                    url_for('points_points', username='Dan', trip='default'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['message'], 'uploaded 1 points')
        self.assertEqual(Point.objects.count(), 1)
        point = Point.objects.first()
        self.assertEqual(point.trip_id, 'testing')

    def test_many_point_submission(self):
        """ test submission of many points """
        pt_json = self._generate_points(5, trip='testing')

        response = self.client.post(
                    url_for('points_points', username='Dan', trip='default'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['message'], 'uploaded 5 points')
        self.assertEqual(Point.objects.count(), 5)
        points = Point.objects.all()
        self.assertTrue(all([p.trip_id == 'testing' for p in points]))

    def test_tripid(self):
        """ test retrieving certain trip points """
        pt_json = self._generate_points(3, trip='trip1')
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))

        pt_json = self._generate_points(2, trip='trip2')
        response = self.client.post(
                    url_for('points_points', username='Dan', trip='trip2'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))

        response = self.client.get(url_for('points_points',
                                           username='Dan',
                                           trip='trip1'))
        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(json_response['points']), 3)

        response = self.client.get(url_for('points_points',
                                           username='Dan',
                                           trip='trip2'))
        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(len(json_response['points']), 2)

    def test_upload_csv(self):
        """ test uploading csv point file """
        # test upload valid file
        data = dict(file=(open('test/data/test_points.csv', 'rb'),
                          "test_points.csv"))
        response = self.client.post(
                    url_for('points_points_csv', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    content_type='multipart/form-data',
                    data=data),
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(response[0].status, '201 CREATED')
        self.assertIn('task_id', json_response)
        # check that the task to insert points and line ran
        self.assertEqual(Line.objects.count(), 1)
        self.assertEqual(Point.objects.count(), 11)

        # test wrong file extension
        data = dict(file=(open('test/data/test_points.csv', 'rb'),
                          "test_points.tsv"))
        response = self.client.post(
                    url_for('points_points_csv', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    content_type='multipart/form-data',
                    data=data),
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(response[0].status, '400 BAD REQUEST')
        self.assertEqual(json_response['message'], 'no csv file')

        # test no file
        data = dict(file=(b'', ''),)
        response = self.client.post(
                    url_for('points_points_csv', username='Dan', trip='trip1'),
                    headers=self._api_headers(),
                    content_type='multipart/form-data',
                    data=data),
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(response[0].status, '400 BAD REQUEST')
        self.assertEqual(json_response['message'], 'no file')
