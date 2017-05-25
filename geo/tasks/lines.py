import math
from cassandra.cqlengine.query import BatchQuery

from geo import create_celery_app
from ..model import Point, Line

celery = create_celery_app()


@celery.task()
def line_from_points(u_t):
    """
    Simplifies points from a trip into a line and stores it in the backend
    Down samples to 1 minute intervals

    u_t: username, trip tuple. Often recieved from a parent task
    """

    def d_approx(lonlat1, lonlat2):
        """ Approximate ditance between two points on a plain """
        # ~ distance of one longitudinal degree at the equator in km
        edist = 110.0
        dlat = lonlat1[1] - lonlat2[1]
        dlon = (lonlat1[0] - lonlat2[0])*math.cos(lonlat1[1])
        return edist*math.sqrt(dlat*dlat + dlon*dlon)

    username, trip = u_t
    q = (Point.objects.filter(Point.username == username)
                      .filter(Point.trip_id == trip))
    points = q.limit(None)
    if len(points) == 0:
        return {'line': {}}
    # this format resolves down to minutes, thus downsampling any finer points
    tfmt = "%Y-%m-%d%H:%M"
    coords = [points[0]]
    for point in points[0:]:
        t1 = point.created_at.strftime(tfmt)
        t2 = coords[-1].created_at.strftime(tfmt)
        if t1 == t2:
            if point.accuracy < coords[-1].accuracy:
                coords[-1] = point
        else:
            d = d_approx((point.lon, point.lat),
                         (coords[-1].lon, coords[-1].lat))
            v = d / (point.created_at - coords[-1].created_at).total_seconds()
            # Only use points averaging > 0.1 km/hr
            # and net displacement of 0.5 km
            if (v*3600.0) > 0.1 and d > 0.5:
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
