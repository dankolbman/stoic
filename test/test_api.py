import time
import json
import unittest
from flask import current_app, url_for
from points import create_app, db

from points.model import Point


class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_keyspace_simple(self.app.config['CASSANDRA_KEYSPACE'], 1)
        db.sync_db()
        d = [p.delete() for p in Point.objects.all()]
        self.client = self.app.test_client()

    def tearDown(self):
        d = [p.delete() for p in Point.objects.all()]
        self.app_context.pop()

    def _api_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_status(self):
        """ Check that the api status is returning 200 """
        response = self.client.get(url_for('api.status'))
        # Check response
        self.assertTrue(response.status_code == 200)
        # Check content of json response status
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['status'] == 200)
        self.assertTrue(json_response['version'] == '1.0')

    def test_points(self):
        """ Test points endpoint """
        self.assertEqual(Point.objects.count(), 0)
        point = Point(geom=[-87.682321, 41.839344],
                      accuracy=10.0,
                      trip_id='default')
        point.save()
        self.assertEqual(Point.objects.count(), 1)

        response = self.client.get(url_for('api.points'))
        # check response
        self.assertEqual(response.status_code, 200)
        # check content of json response status
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['count'], 1)
        self.assertEqual(json_response['count'], len(json_response['points']))

        response = self.client.get(url_for('api.points'),
                                   query_string=dict(as_html=True))
        self.assertTrue('<html>' in str(response.data))

    def test_no_points(self):
        """ Test response for empty post """
        response = self.client.post(
                    url_for('api.upload_points', trip='test', api_key='123'),
                    headers=self._api_headers(),
                    data=json.dumps({}))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertEqual(json_response['message'], 'no points posted')
        self.assertEqual(json_response['status'], 201)

    def test_missing_points(self):
        """ Test response for empty post """
        response = self.client.post(
                    url_for('api.upload_points', trip='test', api_key='123'),
                    headers=self._api_headers(),
                    data=json.dumps({'points': []}))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status, '400 BAD REQUEST')
        self.assertIn('missing', json_response['message'])
        self.assertEqual(json_response['status'], 400)

    def test_pagination(self):
        """ Test pagination of points """
        # add a bunch of points
        pt_json = {
                        'points': [
                            {'latitude': -87.682321,
                             'longitude': 41.839344},
                            {'latitude': -87.682321,
                             'longitude': 41.839344},
                            {'latitude': -87.682321,
                             'longitude': 41.839344},
                            {'latitude': -87.682321,
                             'longitude': 41.839344},
                            {'latitude': -87.682321,
                             'longitude': 41.839344},
                            {'latitude': -87.682321,
                             'longitude': 41.839344},
                            {'latitude': -87.682321,
                             'longitude': 41.839344},
                            {'latitude': -87.682321,
                             'longitude': 41.839344},
                        ]
                  }
        # post points through api
        response = self.client.post(
                    url_for('api.upload_points', trip='test', api_key='123'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        t = time.time()
        # post a second batch of points to get different timestamps
        pt_json = {
                        'points': [
                            {'latitude': -87.682321,
                             'longitude': 41.839344,
                             'created_at': t},
                            {'latitude': -87.682321,
                             'longitude': 41.839344,
                             'created_at': t},
                            {'latitude': -87.682321,
                             'longitude': 41.839344,
                             'created_at': t},
                            {'latitude': -87.682321,
                             'longitude': 41.839344,
                             'created_at': t},
                            {'latitude': -87.682321,
                             'longitude': 41.839344,
                             'created_at': t},
                        ]
                   }
        response = self.client.post(
                    url_for('api.upload_points', trip='test', api_key='123'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        # get the points
        response = self.client.get(
                    url_for('api.points'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['points']), 10)
        self.assertEqual(json_response['count'], 13)
        # Get the second group of points (t > utc epoch)
        response = self.client.get(
                    url_for('api.points'),
                    headers=self._api_headers(),
                    query_string=dict(start=int(t), size=10))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['points']), 5)

    def test_single_point_submission(self):
        """ test submission of single point """
        pt_json = {
                    'points': [
                        {'latitude': -87.684722,
                         'longitude': 41.836944}
                    ]
                  }

        response = self.client.post(
                    url_for('api.upload_points', trip='test', api_key='123'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['message'], 'uploaded 1 points')
        self.assertEqual(Point.objects.count(), 1)
        point = Point.objects.first()
        self.assertEqual(point.accuracy, 100.0)

    def test_many_point_submission(self):
        """ test submission of many points """
        pt_json = {
                        'points': [
                            {'latitude': -87.682322,
                             'longitude': 41.839344,
                             'accuracy': 10.0},
                            {'latitude': -87.682322,
                             'longitude': 41.839344},
                            {'latitude': -87.682322,
                             'longitude': 41.839344},
                            {'latitude': -87.682322,
                             'longitude': 41.839344},
                            {'latitude': -87.682322,
                             'longitude': 41.839344}
                        ]
                    }

        response = self.client.post(
                    url_for('api.upload_points', trip='test', api_key='123'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['message'], 'uploaded 5 points')
        self.assertEqual(Point.objects.count(), 5)
        points = Point.objects.all()
        self.assertEqual([p.accuracy for p in points if p.accuracy != 100.0],
                         [10.0])
