from flask_restplus import Api
from .points import api as lines_api
from .lines import api as points_api

api = Api(
    title='Geo',
    version='1.0',
    description=open('geo/api/README.md').read()
)

api.add_namespace(points_api)
api.add_namespace(lines_api)
