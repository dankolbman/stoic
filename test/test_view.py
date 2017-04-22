import unittest
from flask import current_app, url_for
from app import create_app, db

from app.model import Point


class ViewTestCase(unittest.TestCase):

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

    def test_index(self):
        """ Check the index page """
        response = self.client.get(url_for('index.index'))
        self.assertEqual(response.status, '200 OK')
