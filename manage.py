#!/usr/bin/env python
import os

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from geo import create_app, db
from flask_script import Manager, Shell
from geo.model import Point

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Point=Point)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test(coverage=False):
    """ Run the unit tests and pep8 checks """
    from subprocess import call
    call(["python","-m","pytest","test"])
    call(["python","-m","pytest","--pep8","geo"])


@manager.option('-n', '--npoints', help='Number of points')
@manager.option('-t', '--tripid', help='Trip id')
def random_points(npoints=1, tripid='test trip'):
    """Inserts n random points into the db"""
    import time
    from datetime import datetime
    from geo.model import Point
    from random import random
    from cassandra.cqlengine.query import BatchQuery
    with BatchQuery() as b:
        for i in range(int(npoints)):
            tripid = 'trip{}'.format(i%10)
            pt = Point.batch(b).create(accuracy=25.0,
                                       created_at=datetime.utcnow(), 
                                       trip_id=tripid,
                                       username='Dan',
                                       coord=[random()*90.0,
                                             random()*360.0-180.0])
            if i %100 == 0:
                b.execute()


@manager.option('-f', '--filepath', help='File to load points from')
@manager.option('-u', '--username', help='Username')
@manager.option('-t', '--tripid', help='Trip id')
def load_points(filepath, username='Dan', tripid='trip'):
    """ Load points from file and insert into db """
    from geo.tasks.csv import parse_csv
    print(parse_csv(filepath, username, tripid).run())
    return

@manager.command
def dbbenchmark():
    """ Benchmark the database by inserting many points and querying them """
    import time
    from geo.model import Point
    from random import random
    from cassandra.cluster import Cluster
    from cassandra.cqlengine.query import BatchQuery
    from cassandra.query import SimpleStatement
    cluster = Cluster(app.config['CASSANDRA_HOSTS'])
    session = cluster.connect()
    session.set_keyspace(app.config['CASSANDRA_KEYSPACE'])
    batch_size = 10000
    batches = 10
    for batch in range(batches):
        # insert batch
        t0 = time.time()
        random_points(batch_size, 'trip1')
        t1 = time.time()
        print('Time to insert', batch_size, 'points:', t1-t0)
        # query all points
        query = "SELECT * FROM point"
        statement = SimpleStatement(query, fetch_size=1000)
        pts = sum([ 1 for pt in session.execute(statement)])
        t2 = time.time()
        print('Time to query', pts, 'points:', t2-t1)

@manager.command
def dbinit():
    db.create_keyspace_simple(app.config['CASSANDRA_KEYSPACE'], 1)
    db.sync_db()


@manager.command
def deploy():
    """Run deployment tasks."""
    pass


if __name__ == '__main__':
    manager.run()
