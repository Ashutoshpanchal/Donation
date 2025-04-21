from flask import Blueprint

bp = Blueprint('donations', __name__, url_prefix='/api/donations')

from app.donations import routes 