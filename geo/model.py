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
    lon = db.columns.Float()
    lat = db.columns.Float()

    def to_json(self):
        """ Returns json representation of the point """
        pt_json = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [self.lon, self.lat],
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
        lonlat = point_json['geometry']['coordinates']
        dt = dateutil.parser.parse(defaults['created_at'])
        return Point(lon=lonlat[0],
                     lat=lonlat[1],
                     accuracy=defaults['accuracy'],
                     username=defaults['username'],
                     created_at=dt,
                     trip_id=defaults['trip_id'])


class Line(db.Model):
    username = db.columns.Text(partition_key=True)
    trip_id = db.columns.Text(partition_key=True)
    created_at = db.columns.DateTime(primary_key=True,
                                     default=datetime.utcnow())
    start_at = db.columns.DateTime()
    end_at = db.columns.DateTime()
    coords = db.columns.List(db.columns.List(value_type=db.columns.Float))

    def to_json(self):
        """ Returns json representation of the line """
        pt_json = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [self.coords]
                    },
                    "properties": {
                        "username": self.username,
                        "trip_id": self.trip_id,
                        "created_at": self.created_at.isoformat(),
                        "start_at": self.start_at.isoformat(),
                        "end_at": self.end_at.isoformat()
                    }
                   }

        return pt_json
