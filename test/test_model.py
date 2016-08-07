import json
import unittest
from datetime import datetime

from flask import current_app, url_for
from app import create_app, db
from app.model import Point

import geoalchemy2.functions as func

class ModelTestCase(unittest.TestCase):
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

    def test_point(self):
        ''' Check point model '''
        dt = datetime.utcnow()
        lat = 41.836944
        lon = -87.684722
        point = Point(timestamp=dt,
                      accuracy=25.0,
                      geom='POINT({0} {1})'.format(lat, lon))

        self.assertEqual(point.to_json()['id'], None )
        self.assertEqual(point.to_json()['timestamp'], dt )
        self.assertEqual(point.to_json()['accuracy'], 25.0 )
        self.assertEqual(point.to_json()['geometry']['coordinates'], [lat,lon])

        db.session.add(point)
        self.assertEqual(Point.query.count(), 1)
        # Make sure the postgis geojson matches object's to_json()
        self.assertDictEqual(point.to_json()['geometry'],
                    json.loads(db.session.scalar(func.ST_AsGeoJSON(point.geom))))
