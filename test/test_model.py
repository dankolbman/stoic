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
                      geom=Point.point_geom([lon, lat]),
                      trip='test')

        db.session.add(point)

        db.session.commit()
        point = Point.query.first()
        self.assertEqual(point.to_json()['id'], 1 )
        self.assertEqual(point.to_json()['timestamp'], dt )
        self.assertEqual(point.to_json()['accuracy'], 25.0 )
        self.assertEqual(point.to_json()['geometry']['coordinates'], [lon,lat])

        self.assertEqual(Point.query.count(), 1)
        # Make sure the postgis geojson matches object's to_json()
        self.assertDictEqual(point.to_json()['geometry'],
                {'type': 'Point', 'coordinates': [-87.684722, 41.836944]})
        db.session.delete(point)

        point_json = { 'longitude': lon,
                       'latitude': lat,
                        'accuracy': 15.0 }

        point = Point.from_json(point_json)
        self.assertEqual(point.accuracy, 15.0)
        self.assertEqual(point.timestamp, datetime(1970, 1, 1, 0, 0))
        db.session.add(point)
        self.assertEqual(Point.query.count(), 1)
