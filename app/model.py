from datetime import datetime

from . import db

from geoalchemy2 import Geometry


class Ping(db.Model):
  __tablename__ = "ping"
  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
  accuracy = db.Column(db.Float, default=100.0, nullable=False)
  loc = db.Column(Geometry('POINT'))
