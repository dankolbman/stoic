import uuid
import json
from datetime import datetime
import dateutil.parser

from . import db


class Point(db.Model):
    username = db.columns.Text(partition_key=True)
    trip_id = db.columns.Text(partition_key=True)
    created_at = db.columns.DateTime(primary_key=True,
                                     default=datetime.utcnow())
    point_id = db.columns.UUID(default=uuid.uuid4)
    accuracy = db.columns.Double(default=0.0)
    coord = db.columns.List(value_type=db.columns.Float)

    def to_json(self):
        """ Returns json representation of the point """
        pt_json = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": self.coord
                    },
                    "properties": {
                        "username": self.username,
                        "point_id": str(self.point_id),
                        "trip_id": self.trip_id,
                        "created_at": self.created_at.isoformat(),
                        "accuracy": self.accuracy
                    }
                   }

        return pt_json

    @staticmethod
    def from_json(point_json, trip='default', username='default'):
        """ Creates a new point from a json object """
        now = datetime.utcnow().isoformat()
        defaults = {'accuracy': 0.0,
                    'created_at': now,
                    'trip_id': trip,
                    'username': username}
        defaults.update(point_json['properties'])
        latlon = point_json['geometry']['coordinates']
        dt = dateutil.parser.parse(defaults['created_at'])
        return Point(coord=latlon,
                     accuracy=defaults['accuracy'],
                     username=defaults['username'],
                     created_at=dt,
                     trip_id=defaults['trip_id'])
