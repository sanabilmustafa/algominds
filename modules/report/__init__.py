from flask import Blueprint

report_bp = Blueprint('report', __name__, template_folder='templates', static_folder='static')

from . import report