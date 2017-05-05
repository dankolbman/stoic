from flask import Flask
from flask_profile import Profiler
from flask_cqlalchemy import CQLAlchemy
from flask_restplus import Api
from flask_jwt import JWT
from config import config

db = CQLAlchemy()
profiler = Profiler()


def authenticate(username, password):
    """ We will never authenticate a user from this sevice """
    return None


def identity(payload):
    return payload['identity']


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    db.create_keyspace_simple(app.config['CASSANDRA_KEYSPACE'], 1)
    db.sync_db()
    profiler.init_app(app)
    from .api import api
    api.init_app(app)
    jwt = JWT(app, authenticate, identity)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    return app
