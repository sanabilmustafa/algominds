from flask import Blueprint

strategy_bp = Blueprint('strategy', __name__, template_folder='templates', static_folder='static')

from modules.database import db

from . import strategy
from . import models