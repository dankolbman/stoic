import csv
from cassandra.cqlengine.query import BatchQuery
from dateutil import parser

from . import celery
from ..model import Point
from geo import create_celery_app


@celery.task()
def parse_csv(filepath, username, trip):
    """
    Parse a csv and import to database
    """
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile.read().split('\n'))
        i = 0
        b = BatchQuery()
        last_dt = None
        for i, line in enumerate(reader):
            if i % 1000 == 0:
                b.execute()
                b = BatchQuery()
            try:
                dt = parser.parse(line['time'])
                if dt == last_dt:
                    continue
                pt = {'lon': line['lon'],
                      'lat': line['lat'],
                      'accurracy': line['accuracy'],
                      'username': username,
                      'created_at': dt,
                      'trip_id': trip}
                last_dt = dt
                Point.batch(b).create(**pt)
            except ValueError:
                continue
        b.execute()
    return username, trip
