import uuid
import json
from datetime import datetime
import dateutil.parser

from .import db


class Point(db.Model):
    trip_id = db.columns.Text(primary_key=True)
    created_at = db.columns.DateTime(primary_key=True,
                                     default=datetime.utcnow())
    point_id = db.columns.UUID(default=uuid.uuid4)
    accuracy = db.columns.Double(default=100.0)
    geom = db.columns.List(value_type=db.columns.Float)

    def to_json(self):
        """ Returns json representation of the point """
        pt_json = {
                    'point_id': str(self.point_id),
                    'created_at': self.created_at.isoformat(),
                    'accuracy': self.accuracy,
                    'geometry': {'coordinates': self.geom}
                }

        return pt_json

    @staticmethod
    def from_json(point_json, trip='default'):
        """ Creates a new point from a json object """
        now = datetime.utcnow().isoformat()
        defaults = {'accuracy': 100.0, 'created_at': now, 'trip_id': trip}
        defaults.update(point_json)
        latlon = [point_json['longitude'], point_json['latitude']]
        dt = dateutil.parser.parse(defaults['created_at'])
        return Point(geom=latlon,
                     accuracy=defaults['accuracy'],
                     created_at=dt,
                     trip_id=defaults['trip_id'])
