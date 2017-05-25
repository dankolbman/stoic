import os
from flask import request, jsonify, current_app, abort
from flask_jwt import _jwt_required, JWTError, current_identity
from flask_restplus import Api, Resource, Namespace, fields
from datetime import datetime, timedelta
from dateutil import parser

from ..model import Point


api = Namespace('interp', description='Interpolation service')


@api.route('/status')
class Status(Resource):
    @api.doc(responses={200: 'OK'})
    def get(self, **kwargs):
        """ Service status """
        return {'status': 200, 'version': '1.0'}


@api.route('/<string:username>/<string:trip>')
class Interp(Resource):
    def get(self, username, trip):
        """
        Resolve a coordinate for a given time by interpolating points in a trip
        """
        t = request.args.get('time', None, type=str)
        dt = parser.parse(t)
        start_dt = dt - timedelta(minutes=1)
        end_dt = dt + timedelta(minutes=15)
        q = (Point.objects.filter(Point.username == username)
                  .filter(Point.trip_id == trip)
                  .filter(end_dt >= Point.created_at >= start_dt))
        results = q.limit(5)

        if len(results) == 0:
            abort(400, 'insufficient data')

        # If there is only one point in the time range,
        # or the returned points are somewhere in the future,
        # assign coords from the first result
        if len(results) == 1 or results[0].created_at > end_dt:
            r = Point(created_at=dt,
                      lon=results[0].lon,
                      lat=results[0].lat)
            return {'point': r.to_json()}, 200

        r1 = results[0]
        for r in results[0:]:
            if r.created_at is not r1.created_at:
                r2 = r
                break

        fr = (dt - r1.created_at) / (r2.created_at - r1.created_at)
        lon = r1.lon + fr*(r2.lon-r1.lon)
        lat = r1.lat + fr*(r2.lat-r1.lat)

        r = Point(username=r1.username,
                  trip_id=r1.trip_id,
                  created_at=dt,
                  lon=lon, lat=lat)

        return {'point': r.to_json()}, 200
