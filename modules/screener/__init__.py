from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy

from modules.database import db

screener_bp = Blueprint('screener', __name__, template_folder="templates", static_folder="static")

from . import screener