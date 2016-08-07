from datetime import datetime
from flask import jsonify
from . import db
from geoalchemy2 import Geometry


class Point(db.Model):
    __tablename__ = "point"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    accuracy = db.Column(db.Float, default=100.0, nullable=False)
    geom = db.Column(Geometry(geometry_type='POINT'))

    def to_json(self):
        ''' Returns geojson representation of the point '''
        latlon = self.geom.replace('POINT(','').replace(')','')
        latlon = [float(n) for n in latlon.split(' ') ]
        geom = {'type':'Point', 'coordinates':[latlon[0], latlon[1]] }
        pt_json = {
                    'id': self.id,
                    'timestamp': self.timestamp,
                    'accuracy': self.accuracy,
                    'geometry': geom
                }
        return pt_json

    @staticmethod
    def from_json(point_json):
        ''' Creates a new point from a json object '''
        defaults = {'accuracy': None, 'timestamp': None}
        defaults.update(point_json)
        return Point(geom=Point.point_geom(point_json['coordinates']),
                     accuracy=defaults['accuracy'],
                     timestamp=defaults['timestamp'])

    @staticmethod
    def point_geom(coords):
        ''' Converts list of lat, lon to POINT geometry format '''
        return 'POINT({} {})'.format(coords[0], coords[1])

    def __repr__(self):
        return '<Point: {}>'.format(self.id)
