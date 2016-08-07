import unittest
import json
from flask import current_app, url_for
from app import create_app, db

from app.model import Point


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _api_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_status(self):
        ''' Check that the api status is returning 200 '''
        response = self.client.get(url_for('api.status'))
        # Check response
        self.assertTrue(response.status_code == 200)
        # Check content of json response status
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['status'] == 200)
        self.assertTrue(json_response['version'] == '1.0')

    def test_points(self):
        ''' test points endpoint '''
        point = Point(geom=Point.point_geom([ 41.839344, -87.682321 ]), accuracy=10.0)
        db.session.add(point)
        db.session.commit()
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

    def test_pagination(self):
        ''' test pagination of points '''
        # add a bunch of points
        pt_json = {
                        'points': [
                            { 'coordinates': [ 41.839344, -87.682321 ] },
                            { 'coordinates': [ 41.839344, -87.682321 ] },
                            { 'coordinates': [ 41.839344, -87.682321 ] },
                            { 'coordinates': [ 41.839344, -87.682321 ] },
                            { 'coordinates': [ 41.833244, -87.694221 ] },
                            { 'coordinates': [ 41.837244, -87.682421 ] },
                            { 'coordinates': [ 41.836844, -87.689322 ] },
                            { 'coordinates': [ 41.836344, -87.681422 ] },
                            { 'coordinates': [ 41.839334, -87.682382 ] },
                            { 'coordinates': [ 41.833234, -87.694282 ] },
                            { 'coordinates': [ 41.837234, -87.682482 ] },
                            { 'coordinates': [ 41.836834, -87.689382 ] },
                            { 'coordinates': [ 41.836334, -87.681482 ] },
                        ]
                    }
        # post points through api
        response = self.client.post(
                    url_for('api.new_points'),
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

        response = self.client.get(
                    url_for('api.points'),
                    headers=self._api_headers(),
                    query_string=dict(start=5, size=10))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(len(json_response['points']), 8)


    def test_single_point_submission(self):
        ''' test submission of single point '''
        pt_json = {
                        'points': [
                            { 'coordinates': [ 41.836944, -87.684722 ] }
                        ]
                    }

        response = self.client.post(
                    url_for('api.points'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['message'], 'uploaded 1 points')
        self.assertEqual(Point.query.count(), 1)
        point = Point.query.first()
        self.assertEqual(point.accuracy, 100.0)

    def test_many_point_submission(self):
        ''' test submission of many points '''
        pt_json = {
                        'points': [
                            { 'coordinates': [ 41.839344, -87.682322 ],
                              'accuracy': 10.0 },
                            { 'coordinates': [ 41.833244, -87.694222 ] },
                            { 'coordinates': [ 41.837244, -87.682422 ] },
                            { 'coordinates': [ 41.836844, -87.689322 ] },
                            { 'coordinates': [ 41.836344, -87.681422 ] },
                        ]
                    }

        response = self.client.post(
                    url_for('api.new_points'),
                    headers=self._api_headers(),
                    data=json.dumps(pt_json))
        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(json_response['message'], 'uploaded 5 points')
        self.assertEqual(Point.query.count(), 5)
        point = Point.query.first()
        self.assertEqual(point.accuracy, 10.0)
