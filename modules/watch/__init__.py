from flask import Blueprint

watch_bp = Blueprint('watch', __name__, template_folder='templates', static_folder='static')

from modules.database import db

from . import watch