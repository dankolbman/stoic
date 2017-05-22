from geo import create_celery_app
from cassandra.cqlengine import connection
from celery.signals import worker_process_init

celery = create_celery_app()

# Need to have these after celery to avoid circular deps
from .csv import parse_csv  # noqa
from .lines import line_from_points  # noqa
from config import config  # noqa


@worker_process_init.connect
def open_cassandra_session(*args, **kwargs):
    """ This forces a new connection for every worker """
    connection.setup(celery._conf['CASSANDRA_HOSTS'],
                     celery._conf['CASSANDRA_KEYSPACE'], protocol_version=3)
