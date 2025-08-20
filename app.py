import config
from flask import Flask, render_template
from modules.charting import charting_bp
from modules.userDetails import user_details_bp
from modules.strategy import strategy_bp
from modules.clientAuth import client_auth_bp
from modules.dashboard import dashboard_bp
from modules.dashboard import db
from modules.order import order_bp
from modules.screener import screener_bp
from modules.database import db
from modules.report import report_bp
from modules.watch import watch_bp
# from flask_sock import Sock

app = Flask(__name__)
# sock.init_app(app)

DB_URI = f"postgresql://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

# Set your DB config
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db and register blueprint
db.init_app(app)
app.register_blueprint(charting_bp, url_prefix='/chart')  # Optional prefix
app.register_blueprint(user_details_bp, url_prefix='/user-details')  # Optional prefix
app.register_blueprint(strategy_bp, url_prefix="/strategy")
app.register_blueprint(client_auth_bp, url_prefix='/clientAuth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(order_bp, url_prefix='/order')  # Optional prefix
app.register_blueprint(screener_bp, url_prefix='/screener')  # Optional prefix
app.register_blueprint(report_bp, url_prefix='/reports')  # Optional prefix
app.register_blueprint(watch_bp, url_prefix='/watch')  # Optional prefix


@app.route('/')
def home():
    return render_template('index.html')  

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
