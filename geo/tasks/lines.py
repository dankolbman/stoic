from cassandra.cqlengine.query import BatchQuery

from geo import create_celery_app
from ..model import Point, Line

celery = create_celery_app()


@celery.task()
def line_from_points(u_t):
    """
    Simplifies points from a trip into a line and stores it in the backend

    u_t: username, trip tuple. Often recieved from a parent task
    """
    username, trip = u_t
    q = (Point.objects.filter(Point.username == username)
                      .filter(Point.trip_id == trip))
    points = q.all()
    if len(points) == 0:
        return {'line': {}}

    coords = []
    for point in points:
        if coords == []:
            coords.append(point)
            continue

        if point.created_at.minute == coords[-1].created_at.minute:
            if point.accuracy < coords[-1].accuracy:
                coords[-1] = point
        else:
            coords.append(point)
    start_at = coords[0].created_at
    end_at = coords[-1].created_at
    coords = [[p.lon, p.lat] for p in coords]
    line = Line(username=username,
                trip_id=trip,
                coords=coords,
                start_at=start_at,
                end_at=end_at)
    line.save()
    return u_t
