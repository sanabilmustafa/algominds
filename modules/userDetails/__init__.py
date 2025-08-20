from flask import Blueprint

user_details_bp = Blueprint('user_details', __name__, template_folder='templates', static_folder='static')

from . import submit_form
