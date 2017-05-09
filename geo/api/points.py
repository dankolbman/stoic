import os
import csv
from flask import request, jsonify, current_app
from flask_jwt import _jwt_required, JWTError, current_identity
from flask_restplus import Api, Resource, Namespace, fields
from cassandra.cqlengine.query import BatchQuery
from werkzeug.utils import secure_filename
from datetime import datetime
from dateutil import parser

from ..model import Point


api = Namespace('points', description='Point distribution and consumption')


def belongs_to(username):
    try:
        _jwt_required(None)
        if not current_identity['username'] == username:
            return {'status': 403, 'message': 'not allowed'}, 403
    except JWTError as e:
        return {'status': 403, 'message': 'not allowed'}, 403

    return True


prop_model = api.model('Properties', {
        'trip_id': fields.String(description='Trip UUID'),
        'username': fields.String(description='username'),
        'point_id': fields.String(description='Point UUID'),
        'created_at': fields.DateTime(description='Time of creation'),
        'accuracy': fields.Float(description='Accuracy of the point'),
    })

geom_model = api.model('Geometry', {
        'type': fields.String(description='Geometry type'),
        'coordinates': fields.List(fields.Float, description=('lon, lat pair'))
    })

point_model = api.model('Point', {
        'type': fields.String(description='GeoJSON type'),
        'geometry': fields.Nested(geom_model),
        'properties': fields.Nested(prop_model)
    })

paginated = api.model('PagedPoints', {
        'points': fields.List(fields.Nested(point_model)),
        'count': fields.Integer(description='Number of results')
    })


@api.route('/status')
class Status(Resource):
    @api.doc(responses={200: 'OK'})
    def get(self, **kwargs):
        """ Service status """
        return {'status': 200, 'version': '1.0'}


@api.route('/<string:username>/<string:trip>')
class Points(Resource):
    @api.marshal_with(paginated)
    def get(self, username, trip):
        """
        Retrieve points in GeoJSON format
        """
        epoch = datetime.fromtimestamp(0).isoformat()
        start = request.args.get('start', epoch, type=str)
        start_dt = parser.parse(start)
        size = min(request.args.get('size', 10, type=int), 1000)
        results = (Point.objects.filter(Point.username == username)
                   .filter(Point.trip_id == trip)
                   .filter(Point.created_at >= start_dt)
                   .limit(size))
        total = Point.objects.count()
        return {'points': [r.to_json() for r in results], 'count': total}

    @api.doc(responses={200: 'no points created',
                        201: 'uploaded points',
                        403: 'not allowed',
                        400: 'missing points list in json'})
    def post(self, username, trip):
        """
        Creates points from GeoJSON
        """
        # check the trip belongs to the authenticated user
        allowed = belongs_to(username)
        if allowed is not True:
            return allowed
        points = request.json
        if not points:
            return {'status': 200, 'message': 'no points created'}, 200

        # validate
        if 'points' in points and not points['points']:
            return {'status': 400, 'message':
                    'missing points list in json'}, 400

        points = points['points']
        for point in points:
            p = Point.from_json(point, username=username, trip=trip)
            p.save()

        return {'status': 201,
                'message': 'uploaded {} points'.format(len(points))}, 201


@api.route('/<string:username>/<string:trip>/csv')
class PointsCSV(Resource):
    def get(self, username, trip):
        """
        Retrieve points in CSV format (not implemented yet)
        """
        return {'status': '404', 'message': 'not implemented'}

    @api.doc(responses={200: 'no points created',
                        201: 'uploaded csv file',
                        403: 'not allowed',
                        400: 'no csv file'})
    def post(self, username, trip):
        """
        Uploads points to CSV for processing
        """
        # check the trip belongs to the authenticated user
        allowed = belongs_to(username)
        if allowed is not True:
            return allowed
        # check that there is a file in the request
        if 'file' not in request.files or request.files['file'].filename == '':
            return {'status': 400, 'message': 'no file'}, 400
        csvfile = request.files['file']
        # check that it is a csv file
        if not csvfile or not csvfile.filename.endswith('.csv'):
            return {'status': 400, 'message': 'no csv file'}, 400

        filename = '_'.join([username,
                             trip,
                             secure_filename(csvfile.filename)])
        filepath = os.path.join(current_app.config['CSV_UPLOAD_DIR'], filename)
        csvfile.save(filepath)
        # queue a task to process the points
        # need to import here to avoid circular dependencies
        from ..tasks.csv import parse_csv
        task_id = str(parse_csv.delay(filepath, username, trip))

        return {'status': 201,
                'message': 'uploaded csv file for processing',
                'task_id': task_id}, 201
