from cassandra.cqlengine.query import BatchQuery

from geo import create_celery_app
from ..model import Point, Line

celery = create_celery_app()


@celery.task()
def line_from_points(username, trip):
    """
    Simplifies points from a trip into a line and stores it in the backend
    """
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
    coords = [c.coord for c in coords]
    line = Line(username=username,
                trip_id=trip,
                coords=coords,
                start_at=start_at,
                end_at=end_at)
    line.save()
