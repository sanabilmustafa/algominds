import multiprocessing
import time
from modules.datafeed.feed_manager import run_datafeed
# from modules.strategy_engine.strategy_subscriptions import run_strategies
from modules.clients.clients_server import run_client_server


def start_datafeed():
    print("Starting datafeed...")
    run_datafeed()

# def start_strategy_engine():
#     print("Starting strategy engine...")
#     run_strategy_engine()

def start_client_server():
    print("Starting client server...")
    run_client_server()

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=start_datafeed)
    # p2 = multiprocessing.Process(target=run_strategies)
    p3 = multiprocessing.Process(target=start_client_server)

    p1.start()
    # p2.start()
    p3.start()

    print("Backend processes started. Flask app can run independently.")

    # Optional: Wait for them to complete (or not)
    p1.join()
    # p2.join()
    p3.join()


















# # from modules.strategy_engine.strategy_runner import run_strategy_engine

# # if __name__ == "__main__":
# #     # Execute the strategy engine's run function
# #     run_strategy_engine() 
# from flask import Flask
# from multiprocessing import Process

# from modules.strategy_engine.strategy_runner import run_strategy_engine
# from modules.datafeed.feed_manager import run_datafeed
# import config
# # # Create a minimal Flask app
# # app = Flask(__name__)
# # app.config.from_object('config.Config')  # or wherever your DB URI is defined

# # # Initialize db with this app
# # db.init_app(app)
# # db = SQLAlchemy()
# from modules.strategy_engine import db
# from modules.datafeed import db

# # app = Flask(__name__)
# from app import app

# DB_URI = f"postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

# # Set your DB config
# app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db.init_app(app)
# if __name__ == "__main__":
#     # Strategy Engine
#     strategy_process = Process(target=run_strategy_engine)
#     strategy_process.start()

#     # Data Feed Server
#     datafeed_process = Process(target=run_datafeed)
#     datafeed_process.start()

#     # Keep processes running
#     strategy_process.join()
#     datafeed_process.join()

# # with app.app_context():
# #     run_strategy_engine()