from flask_restplus import Api
from .v1 import api as v1

api = Api(
    title='Points',
    version='1.0',
    description='Geocoordinate point service'
)

api.add_namespace(v1)
