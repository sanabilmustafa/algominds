# from flask import Blueprint
# from flask_sqlalchemy import SQLAlchemy
# import threading
# import time
# from datetime import datetime
# from .state import run_datafeed
# datafeed_bp = Blueprint('datafeed', __name__)

# db = SQLAlchemy()
# datafeed_thread = threading.Thread(target=run_datafeed, daemon=True)

# def is_market_open():
#     # Pakistan Stock Exchange hours: 9:30 AM to 3:30 PM (Mon–Fri)
#     now = datetime.now()
#     return now.weekday() < 5 and (now.hour == 9 and now.minute >= 30 or 10 <= now.hour < 15)

# @datafeed_bp.before_app_request
# def start_datafeed():
#     if is_market_open():
#         if not datafeed_thread.is_alive():
#             print("🚀 Launching datafeed thread...")
#             datafeed_thread.start()
#     else:
#         print("Market is closed. Datafeed thread will not start.")
        


# from . import state, utils

