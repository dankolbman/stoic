from flask import jsonify

from .. import db
from flask import Blueprint

api = Blueprint('api', __name__)

API_VERSION = '1.0'

@api.route('/', methods=['GET'])
def status():
    return jsonify({ 'status': 200, 'version': API_VERSION })
