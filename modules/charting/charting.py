from flask import  jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime, time
from . import charting_bp, db
from modules.strategy.models import Historical

# collection of all the routes:
# @charting_bp.route('/time')
# @charting_bp.route('/config')
# @charting_bp.route('/symbols', methods=['GET'])
# @charting_bp.route("/symbol_info")
# @charting_bp.route('/search')
# @charting_bp.route('/history')

# Define the Historical Model
# class Historical(db.Model):
#     """
#     Represents the 'historical' table in the database.
#     Stores historical stock data.
#     """
#     __tablename__ = 'historical'
    
#     id = db.Column(db.Integer, primary_key=True)
#     stock_id = db.Column(db.Integer, nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     open = db.Column(db.Numeric(10,2), nullable=False)
#     high = db.Column(db.Numeric(10,2), nullable=False)
#     low = db.Column(db.Numeric(10,2), nullable=False)
#     close = db.Column(db.Numeric(10,2), nullable=False)
#     volume = db.Column(db.Numeric(10,2), nullable=False)
#     symbol = db.Column(db.String(50), nullable=True)


@charting_bp.route('/time')
def get_time():
    from time import time
    return jsonify({"time": int(time())})

@charting_bp.route('/config')
def config():
    return jsonify({
        "supports_search": True,
        "supports_group_request": True,
        "supports_marks": False,
        "supports_timescale_marks": False,
        "supports_time": True,
        "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W"]
    })

@charting_bp.route('/symbols', methods=['GET'])
def get_symbols():
    symbol = request.args.get('symbol', '').upper()

    if not symbol:
        return jsonify({"s": "error", "errmsg": "Missing symbol"}), 400

    # Check if symbol exists in DB
    exists = db.session.query(Historical).filter(Historical.symbol == symbol).first()
    if not exists:
        return jsonify({"s": "error", "errmsg": "Symbol not found"}), 404

    return jsonify({
        "name": symbol,
        "ticker": symbol,
        "description": f"{symbol} Stock",
        "type": "stock",
        "exchange": "PSX",
        "minmov": 1,
        "pricescale": 100,
        "has_intraday": True,
        "has_no_volume": False,
        "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W"],
    })

@charting_bp.route("/symbol_info")
def symbol_info():
    symbols = db.session.query(Historical.symbol).distinct().all()
    symbol_list = [s[0] for s in symbols]

    return jsonify({
            "s": "ok",
            "symbol": symbol_list,
            "description": [f"{s} Stock" for s in symbol_list],
            "exchange-listed": ["PSX"] * len(symbol_list),
            "exchange-traded": ["PSX"] * len(symbol_list),
            "minmovement": [1] * len(symbol_list),
            "pricescale": [100] * len(symbol_list),
            "has_intraday":  [True] * len(symbol_list),
            "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W"] * len(symbol_list),
            "type": ["stock"] * len(symbol_list),
            "timezone": ["Asia/Karachi"] * len(symbol_list),
    })

@charting_bp.route('/search')
def search():
    query = request.args.get('query', '').upper()
    limit = int(request.args.get('limit', 30))

    results = db.session.query(Historical.symbol).filter(
        Historical.symbol.ilike(f"{query}%")
    ).distinct().limit(limit).all()

    return jsonify([
        {
            "symbol": symbol[0],
            "full_name": symbol[0],
            "description": f"{symbol[0]} Stock",
            "exchange": "PSX",
            "ticker": symbol[0],
            "type": "stock"
        }
        for symbol in results
    ])


@charting_bp.route('/history')
def get_stock_data():
    symbol = request.args.get('symbol')

    if not symbol:
        return jsonify({"s": "error", "errmsg": "Missing symbol"})

    stock_rows = Historical.query.filter(
        Historical.symbol == symbol,
    ).order_by(Historical.date.asc()).all()


    if not stock_rows:
        return jsonify({"s": "no_data"})

    return jsonify({
        "s": "ok",
        "t": [
            int(datetime.combine(row.date, time(12, 0)).timestamp()) 
            for row in stock_rows
            ],
        "o": [float(row.open) for row in stock_rows],
        "h": [float(row.high) for row in stock_rows],
        "l": [float(row.low) for row in stock_rows],
        "c": [float(row.close) for row in stock_rows],
        "v": [float(row.volume) for row in stock_rows]
    })
    
    
@charting_bp.route('/')
def chart_home():
    return render_template('charting.html')
