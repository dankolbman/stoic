import os
from flask import request, jsonify, current_app
from flask_jwt import _jwt_required, JWTError, current_identity
from flask_restplus import Api, Resource, Namespace, fields
from cassandra.cqlengine.query import BatchQuery
from werkzeug.utils import secure_filename
from datetime import datetime
from dateutil import parser

from ..model import Point


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

paginated = api.model('PagedPoints', {
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

        `?size` will limit the number of points in the LineString
        `?start` will determine the time of the first point in the LineString

        For now, we'll generate LineStrings from points. In the future, trip
        LineStrings will be generated from simplified points by another task.
        """
        epoch = datetime.fromtimestamp(0).isoformat()
        start = request.args.get('start', epoch, type=str)
        start_dt = parser.parse(start)
        size = min(request.args.get('size', 100, type=int), 100000)
        points = (Point.objects.filter(Point.username == username)
                  .filter(Point.trip_id == trip)
                  .filter(Point.created_at >= start_dt)
                  .limit(size))
        lines = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [pt.coord for pt in points]
                },
                "properties": {
                    "start_at": points[0].created_at,
                    "end_at": points[-1].created_at,
                    "trip_id": trip,
                    "username": username
                }
        }
        # We only return the one line for now
        return {'lines': [lines], 'count': 1}
