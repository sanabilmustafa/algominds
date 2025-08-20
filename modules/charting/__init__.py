from flask import Blueprint
print("✅ charting_bp routes loaded from init")
from flask_cors import CORS 

charting_bp = Blueprint('charting', __name__, template_folder='templates', static_folder='static')
CORS(charting_bp) 
from modules.database import db

from . import charting
