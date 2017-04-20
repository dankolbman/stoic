import json
import unittest
from datetime import datetime

from flask import current_app, url_for
from app import create_app, db
from app.model import Point

from cassandra.cqlengine.management import create_keyspace_simple


class ModelTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_keyspace_simple(self.app.config['CASSANDRA_KEYSPACE'], 1)
        db.sync_db()
        d = [ p.delete() for p in Point.objects.all()]
        self.client = self.app.test_client()

    def tearDown(self):
        d = [ p.delete() for p in Point.objects.all()]
        self.app_context.pop()

    def test_point(self):
        """ Check point model """
        dt = datetime.utcnow()
        lat = 41.836944
        lon = -87.684722
        point = Point.create(created_at=dt,
                      accuracy=25.0,
                      geom=[lat, lon],
                      trip_id='default')
        point.save()
        point = Point.objects().limit(1)[0]

        self.assertEqual(Point.objects().count(), 1)
        js = point.to_json()
        self.assertEqual(js['point_id'], str(point.point_id))
        # Cassandra will lose precision on dates
        self.assertEqual(js['created_at'][:-4], dt.isoformat()[:-4])
        self.assertEqual(point.to_json()['accuracy'], 25.0 )
        # Cassandra will return exact float representation
        self.assertAlmostEqual(js['geometry']['coordinates'][0], lat, 5)
        self.assertAlmostEqual(js['geometry']['coordinates'][1], lon, 5)

        point_json = { 'longitude': lon,
                       'latitude': lat,
                       'accuracy': 15.0 }

        point = Point.from_json(point_json)
        self.assertEqual(point.accuracy, 15.0)
        self.assertEqual(point.created_at, datetime(1970, 1, 1, 0, 0))
        self.assertEqual(Point.objects.count(), 1)
