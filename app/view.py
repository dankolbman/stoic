from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app

from app.model import db
from app.model import Point
from geoalchemy2 import Geometry

from sqlalchemy import desc

import os
import json
main = Blueprint('index', __name__)

@main.route('/')
def index():
    """ Home page """
    results = Point.query.order_by(desc(Point.timestamp)).limit(10000).all()
    data = {'coordinates': [ point.to_json()['geometry']['coordinates']
							for point in results],
			'type':'LineString'}

    return render_template('index.html', geo_json=json.dumps(data))
