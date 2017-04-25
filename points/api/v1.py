from flask import request, jsonify
from ..model import Point
from flask_restplus import Api, Resource, Namespace, fields
from datetime import datetime


api = Namespace('points', description='Point operations V1')

model = api.model('Point', {
        'point_id': fields.String(description='Point UUID'),
        'created_at': fields.DateTime(description='Time of creation'),
        'trip_id': fields.String(description='Trip UUID'),
        'accuracy': fields.Float(description='Accuracy of the point'),
        'geom': fields.List(fields.Float, description=('lat, lon pair'))
    })

paginated = api.model('PagedPoints', {
        'points': fields.List(fields.Nested(model)),
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
        """ Retrieves points """
        start = request.args.get('start', 0, type=int)
        start_dt = datetime.utcfromtimestamp(start)
        size = min(request.args.get('size', 10, type=int), 1000)
        results = (Point.objects.filter(Point.created_at >= start_dt)
                   .allow_filtering().limit(size))
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
