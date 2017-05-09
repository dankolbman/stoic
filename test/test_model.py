import json
import unittest
from datetime import datetime

from flask import current_app, url_for

from geo import create_app, db
from geo.model import Point

from utils import FlaskTestCase


class ModelTestCase(FlaskTestCase):

    def test_point(self):
        """ Check point model """
        dt = datetime.utcnow()
        lat = 41.836944
        lon = -87.684722
        point = Point.create(username='Dan',
                             created_at=dt,
                             accuracy=25.0,
                             coord=[lat, lon],
                             trip_id='default')
        point.save()
        point = Point.objects().limit(1)[0]

        self.assertEqual(Point.objects().count(), 1)
        js = point.to_json()
        self.assertEqual(js['properties']['point_id'], str(point.point_id))
        # Cassandra will lose precision on dates
        self.assertEqual(js['properties']['created_at'][:-4],
                         dt.isoformat()[:-4])
        self.assertEqual(js['properties']['accuracy'], 25.0)
        # Cassandra will return exact float representation
        self.assertAlmostEqual(js['geometry']['coordinates'][0], lat, 5)
        self.assertAlmostEqual(js['geometry']['coordinates'][1], lon, 5)

        point_json = {"geometry": {"coordinates": [lon, lat]},
                      "properties": {"username": "dan",
                                     "accuracy": 15.0}}

        point = Point.from_json(point_json)
        self.assertEqual(point.accuracy, 15.0)
        self.assertAlmostEqual(int(point.created_at.timestamp()),
                               int(dt.timestamp()), 1)
        self.assertEqual(Point.objects.count(), 1)
