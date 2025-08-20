from flask import Blueprint

from modules.database import db

order_bp = Blueprint('order', __name__, template_folder="templates", static_folder="static")

from . import order