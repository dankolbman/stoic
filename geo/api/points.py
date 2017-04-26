from flask import request, jsonify
from ..model import Point
from flask_restplus import Api, Resource, Namespace, fields
from datetime import datetime
import dateutil.parser


api = Namespace('points', description='Point operations V1')


prop_model = api.model('Properties', {
        'trip_id': fields.String(description='Trip UUID'),
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
    def get(self, **kwargs):
        return {'status': 200, 'version': '1.0'}


@api.route('/')
class Points(Resource):
    @api.marshal_with(paginated)
    def get(self, **kwargs):
        """
        Retrieve points in GeoJSON format
        """
        epoch = datetime.fromtimestamp(0).isoformat()
        start = request.args.get('start', epoch, type=str)
        trip = request.args.get('trip', 't', type=str)
        start_dt = dateutil.parser.parse(start)
        size = min(request.args.get('size', 10, type=int), 1000)
        results = (Point.objects.filter(Point.trip_id == trip)
                   .filter(Point.created_at >= start_dt)
                   .limit(size))
        total = Point.objects.count()
        return {'points': list(results), 'count': total}

    def put(self, **kwargs):
        """ Creates points and inserts to the database """
        points = request.json
        if not points:
            return {'status': 200, 'message': 'no points created'}, 200

        # Validate
        if 'points' in points and not points['points']:
            return {'status': 400, 'message':
                    'missing points list in json'}, 400

        points = points['points']
        for point in points:
            p = Point.from_json(point)
            p.save()

        return {'status': 201,
                'message': 'uploaded {} points'.format(len(points))}, 201
