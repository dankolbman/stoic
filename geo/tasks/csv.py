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
        for i, line in enumerate(reader):
            if i % 1000 == 0:
                b.execute()
                b = BatchQuery()
            try:
                pt = {'coord': [line['lon'], line['lat']],
                      'accurracy': line['accuracy'],
                      'username': username,
                      'created_at': parser.parse(line['time']),
                      'trip_id': trip}
                Point.batch(b).create(**pt)
            except ValueError:
                continue
        b.execute()
    return i
