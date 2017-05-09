from flask_restplus import Api
from .points import api as v1

api = Api(
    title='Geo',
    version='1.0',
    description=open('geo/api/README.md').read()
)

api.add_namespace(v1)
