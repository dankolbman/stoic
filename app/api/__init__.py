from flask import jsonify, request
from flask import Blueprint

import json

from .. import db
from ..model import Point


api = Blueprint('api', __name__)

API_VERSION = '1.0'

@api.route('/', methods=['GET'])
def status():
    return jsonify({ 'status': 200, 'version': API_VERSION })

@api.route('/points', methods=['GET'])
def points():
    points = []
    # TODO: limit and offset of query should be inputs
    for pt in Point.query.limit(1000).all():
        points.append(json.loads(
            db.session.scalar(pt.geom.ST_AsGeoJSON())))
    return jsonify({'points': points})

@api.route('/points', methods=['POST'])
def new_points():
    points = request.json
    # Validate
    if 'points' not in points and points['points'] is list:
        return jsonify({'status': 400,
                        'message': 'Missing points list in posted json'}), 400
    points = points['points']
    for point in points:
        p = Point.from_json(point)
        db.session.add(p)
    db.session.commit()
    return jsonify({'status': 201,
                    'message': 'uploaded {} points'.format(len(points))}), 201
