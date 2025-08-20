from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

from modules.database import db

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

from . import dashboard

