#!/usr/bin/env python
import os

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.model import Point

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, Point=Point)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('test')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def random_points(n=1):
    """Inserts n random points into the db"""
    from app.model import Point
    from random import random
    for i in range(n):
        pt = Point(accuracy=25.0, geom='POINT({} {})'.format(
                        random()*90.0, random()*360.0-180.0))
        db.session.add(pt)
    db.session.commit()

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade

    # migrate database to latest revision
    upgrade()


if __name__ == '__main__':
    manager.run()
