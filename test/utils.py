import jwt
import unittest
from geo import create_app, db
from geo.model import Point, Line


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_keyspace_simple(self.app.config['CASSANDRA_KEYSPACE'], 1)
        db.sync_db()
        self.client = self.app.test_client()

    def tearDown(self):
        d = [p.delete() for p in Point.objects.all()]
        d = [l.delete() for l in Line.objects.all()]
        self.app_context.pop()

    def _api_headers(self, username='Dan'):
        """
        Returns headers for a json request along with a JWT for authenticating
        as a given user
        """
        auth = jwt.encode({"identity": {"username": username},
                           "nbf": 1493862425,
                           "exp": 9999999999,
                           "iat": 1493862425},
                          'secret', algorithm='HS256')
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'JWT ' + auth.decode('utf-8')
        }
