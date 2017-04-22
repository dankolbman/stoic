import uuid
import json
from datetime import datetime

from . import db


class Point(db.Model):
    point_id = db.columns.UUID(primary_key=True, default=uuid.uuid4)
    created_at = db.columns.DateTime(primary_key=True, default=datetime.utcnow())
    trip_id = db.columns.Text()
    accuracy = db.columns.Double(default=100.0)
    geom = db.columns.List(value_type=db.columns.Float)

    def to_json(self):
        """ Returns json representation of the point """
        pt_json = {
                    'point_id': str(self.point_id),
                    'created_at': self.created_at.isoformat(),
                    'accuracy': self.accuracy,
                    'geometry': { 'coordinates':self.geom }
                }

        return pt_json

    @staticmethod
    def from_json(point_json, trip='default'):
        """ Creates a new point from a json object """
        defaults = {'accuracy': 100.0, 'created_at': 0, 'trip_id': trip}
        defaults.update(point_json)
        latlon = [ point_json['longitude'], point_json['latitude'] ]
        ts = datetime.utcfromtimestamp(defaults['created_at'])
        return Point(geom=latlon,
                     accuracy=defaults['accuracy'],
                     created_at=ts,
                     trip_id=defaults['trip_id'])
