import os
from flask import request, jsonify, current_app
from flask_jwt import _jwt_required, JWTError, current_identity
from flask_restplus import Api, Resource, Namespace, fields
from cassandra.cqlengine.query import BatchQuery
from werkzeug.utils import secure_filename
from datetime import datetime
from dateutil import parser

from ..model import Line


api = Namespace('lines', description='Line distribution and consumption')


prop_model = api.model('Properties', {
        'trip_id': fields.String(description='Trip UUID'),
        'username': fields.String(description='username'),
        'start_at': fields.DateTime(description='Time of first point'),
        'end_at': fields.DateTime(description='Time of last point'),
    })

geom_model = api.model('Geometry', {
        'type': fields.String(description='Geometry type'),
        'coordinates': fields.List(fields.List(
                        fields.Float, description=('lon, lat pair')))
    })

line_model = api.model('Line', {
        'type': fields.String(description='GeoJSON type'),
        'geometry': fields.Nested(geom_model),
        'properties': fields.Nested(prop_model)
    })

paginated = api.model('PagedLines', {
        'lines': fields.List(fields.Nested(line_model)),
        'count': fields.Integer(description='Number of results')
    })


@api.route('/status')
class Status(Resource):
    @api.doc(responses={200: 'OK'})
    def get(self, **kwargs):
        """ Service status """
        return {'status': 200, 'version': '1.0'}


@api.route('/<string:username>/<string:trip>')
class Lines(Resource):
    @api.marshal_with(paginated)
    def get(self, username, trip):
        """
        Retrieve lines in GeoJSON format

        At most, there should only be one line for any given user, trip
        """
        q = (Line.objects.filter(Line.username == username)
                         .filter(Line.trip_id == trip))
        lines = q.limit(1)
        if len(lines) == 0:
            return {'lines': [], 'count': 0}

        lines = lines[0].to_json()

        # We only return the one line for now
        return {'lines': [lines], 'count': 1}
