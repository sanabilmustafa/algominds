from flask import Blueprint
print("✅ clientAuth routes loaded from init")

client_auth_bp = Blueprint('client_auth', __name__, template_folder='templates', static_folder='static')

from . import clientAuth