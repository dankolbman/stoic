from flask import Flask
from flask_profile import Profiler
from flask_cqlalchemy import CQLAlchemy
from config import config

db = CQLAlchemy()
profiler = Profiler()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    profiler.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .api import api as api_blueprint
    from .view import main as main_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    app.register_blueprint(main_blueprint)

    return app
