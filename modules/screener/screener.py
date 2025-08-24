


from flask import render_template
from . import screener_bp, db
import json

from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_sock import Sock
from flask_cors import CORS
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

# from modules.database import db
# from modules.screener.models import ScreenerProfile, ScreenerProfileItem, Stock
class Screener(db.Model):
    __tablename__ = 'screener'

    screener_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Screener {self.screener_id}>"


class ScreenerProfile(db.Model):
    __tablename__ = 'screener_profile'

    profile_id = db.Column(db.Integer, primary_key=True)
    screener_id = db.Column(db.Integer, db.ForeignKey('screener.screener_id'), nullable=False)
    profile_name = db.Column(db.String, nullable=False)
    filters = db.Column(JSONB, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_default = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f"<ScreenerProfile {self.profile_name}>"

from sqlalchemy.dialects.postgresql import JSONB

class ScreenerProfileItem(db.Model):
    __tablename__ = 'screener_profile_items'

    item_id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('screener_profile.profile_id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.stock_id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    selected_columns = db.Column(JSONB)
    indicators = db.Column(JSONB)

    stock = relationship('Stock', backref='profile_items')  # <-- add this

    __table_args__ = (
        db.UniqueConstraint('profile_id', 'stock_id', name='unique_profile_stock'),
    )

    def __repr__(self):
        return f"<ScreenerProfileItem Profile: {self.profile_id}, Stock: {self.stock_id}>"


class Stock(db.Model):
    __tablename__ = 'stock'

    stock_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    sector = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Stock {self.symbol}>"
    
    
sock = Sock()
clients = []

CORS(screener_bp)

@screener_bp.route('/', defaults={'profile_id': None})
@screener_bp.route('/<int:profile_id>')
def index(profile_id):
    # 🟨 STEP 1: Redirect to default profile if no ID is in the URL
    if profile_id is None:
        default_profile = ScreenerProfile.query.filter_by(is_default=True).first()
        if default_profile:
            return redirect(url_for('screener.index', profile_id=default_profile.profile_id))
        else:
            return "No default profile set", 404

    # 🟨 STEP 2: Load stock symbols from JSON
    with open('modules/screener/stocks.json') as f:
        raw_symbols = json.load(f)

    stock_symbols = []
    for item in raw_symbols:
        parts = item.split(" - ")
        if len(parts) >= 2:
            symbol = parts[0].strip()
            label = item.strip()
            stock_symbols.append({"value": symbol, "label": label})
        else:
            stock_symbols.append({"value": item.strip(), "label": item.strip()})

    # 🟨 STEP 3: Render template with profile_id passed to JS
    return render_template(
        'screener.html',
        stock_symbols=stock_symbols,
        selected_profile_id=profile_id
    )
# # ========= HTML VIEW ===========
# @screener_bp.route('/')
# def index():
#     with open('modules/screener/stocks.json') as f:
#         raw_symbols = json.load(f)

#     stock_symbols = []
#     for item in raw_symbols:
#         parts = item.split(" - ")
#         if len(parts) >= 2:
#             symbol = parts[0].strip()
#             label = item.strip()
#             stock_symbols.append({"value": symbol, "label": label})
#         else:
#             # fallback if no company name
#             stock_symbols.append({"value": item.strip(), "label": item.strip()})

#     return render_template('screener.html', stock_symbols=stock_symbols)


# ========= WEBSOCKET ===========
@sock.route('/screener/ws')
def feed_socket(ws):
    clients.append(ws)
    print("🟢 Screener client connected.")
    try:
        while True:
            data = ws.receive()
            print(data)
            if data is None:
                break
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        clients.remove(ws)
        print("🔴 Screener client disconnected.")


# ========= API ROUTES ==========

@screener_bp.route('/api/stocks/symbols')
def get_symbols():
    try:
        symbols = db.session.query(Stock.symbol).distinct().order_by(Stock.symbol).all()
        return jsonify([row[0] for row in symbols])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@screener_bp.route('/api/stocks/sectors')
def get_sectors():
    try:
        sectors = db.session.query(Stock.sector).distinct().all()
        return jsonify([row[0] for row in sectors])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@screener_bp.route('/api/get_profiles')
def get_profiles():
    try:
        profiles = db.session.query(ScreenerProfile).filter_by(screener_id=1).all()
        return jsonify([
    {
        'id': p.profile_id,
        'name': p.profile_name,
        'is_default': p.is_default  # Include this
    } for p in profiles
])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Inside screener_bp (same as your other routes)
@screener_bp.route('/api/profile-subscription-data/<int:profile_id>')
def get_profile_subscription_data(profile_id):
    try:

        items = (
            db.session.query(ScreenerProfileItem)
            .join(Stock, ScreenerProfileItem.stock_id == Stock.stock_id)
            .filter(ScreenerProfileItem.profile_id == profile_id)
            .all()
        )

        symbols = []
        indicators_set = set()
        selected_columns = set()

        for item in items:
            if item.stock and item.stock.symbol:
                symbols.append(item.stock.symbol)

            if item.indicators:
                indicators_set.update(item.indicators)
            if item.selected_columns:
                selected_columns.update(item.selected_columns)

        return jsonify({
            "symbols": symbols,
            "indicators": list(indicators_set),
            "selected_columns": list(selected_columns)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@screener_bp.route('/api/get_profile_stocks/<int:profile_id>')
def get_profile_stocks(profile_id):
    try:
        stocks = db.session.query(Stock.symbol).join(ScreenerProfileItem, Stock.stock_id == ScreenerProfileItem.stock_id) \
            .filter(ScreenerProfileItem.profile_id == profile_id).all()
        return jsonify([row[0] for row in stocks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@screener_bp.route('/api/create_profile', methods=['POST'])
def create_profile():
    print("create profile function")
    data = request.get_json()
    profile_name = data.get('profile_name')
    symbols = data.get('stocks', [])
    is_default = data.get('is_default', False)
    screener_id = 1  # TODO: make dynamic later
    selected_columns = data.get("selected_columns", [])
    indicators = data.get("indicators", [])

    if not profile_name or not symbols:
        return jsonify({'error': 'Profile name and stocks are required'}), 400

    try:
        if is_default:
            db.session.query(ScreenerProfile).filter_by(
                screener_id=screener_id, is_default=True
            ).update({'is_default': False})

        # ✅ Remove selected_columns here
        new_profile = ScreenerProfile(
            profile_name=profile_name,
            screener_id=screener_id,
            is_default=is_default
        )
        db.session.add(new_profile)
        db.session.flush()  # to get new_profile.profile_id

        stock_ids = dict(db.session.query(Stock.symbol, Stock.stock_id)
                         .filter(Stock.symbol.in_(symbols)).all())

        for symbol in symbols:
            stock_id = stock_ids.get(symbol)
            if stock_id:
                # ✅ Add selected_columns here
                db.session.add(ScreenerProfileItem(
                    profile_id=new_profile.profile_id,
                    stock_id=stock_id,
                    selected_columns=selected_columns,
                    indicators=indicators
                ))
        print("the stocks are", stock_id)
        db.session.commit()
        return jsonify({'message': 'Profile created successfully', 'profile_id': new_profile.profile_id})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@screener_bp.route('/api/update_profile/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    data = request.get_json()
    profile_name = data.get('profile_name')
    symbols = set(data.get('stocks', []))
    is_default = data.get('is_default', False)
    selected_columns = data.get('selected_columns', [])
    indicators = data.get("indicators", [])
    screener_id = 1  # TODO: make dynamic later

    if not profile_name:
        return jsonify({'error': 'Profile name is required'}), 400

    try:
        profile = db.session.query(ScreenerProfile).filter_by(profile_id=profile_id).first()
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        profile.profile_name = profile_name
        profile.is_default = is_default

        if is_default:
            db.session.query(ScreenerProfile).filter(
                ScreenerProfile.screener_id == screener_id,
                ScreenerProfile.profile_id != profile_id
            ).update({'is_default': False})

        # Fetch existing ScreenerProfileItems with stocks
        existing_items = db.session.query(ScreenerProfileItem).join(Stock).filter(
            ScreenerProfileItem.profile_id == profile_id
        ).all()

        # Create a dict mapping symbol to item
        existing_symbols_map = {item.stock.symbol: item for item in existing_items}

        symbols_to_add = symbols - set(existing_symbols_map.keys())
        symbols_to_remove = set(existing_symbols_map.keys()) - symbols
        symbols_to_update = symbols & set(existing_symbols_map.keys())

        # Remove unwanted stocks
        if symbols_to_remove:
            db.session.query(ScreenerProfileItem).filter(
                ScreenerProfileItem.profile_id == profile_id,
                ScreenerProfileItem.stock_id.in_(
                    db.session.query(Stock.stock_id).filter(Stock.symbol.in_(symbols_to_remove))
                )
            ).delete(synchronize_session=False)

        # Update existing stocks with new columns & indicators
        for symbol in symbols_to_update:
            item = existing_symbols_map[symbol]
            item.selected_columns = selected_columns
            item.indicators = indicators

        # Add new stocks with selected_columns and indicators
        if symbols_to_add:
            symbol_to_id = dict(db.session.query(Stock.symbol, Stock.stock_id)
                                .filter(Stock.symbol.in_(symbols_to_add)).all())
            for symbol in symbols_to_add:
                stock_id = symbol_to_id.get(symbol)
                if stock_id:
                    db.session.add(ScreenerProfileItem(
                        profile_id=profile_id,
                        stock_id=stock_id,
                        selected_columns=selected_columns,
                        indicators=indicators
                    ))

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@screener_bp.route('/api/get_profile_meta/<int:profile_id>', methods=['GET'])
def get_profile_meta(profile_id):
    # Fetch one ScreenerProfileItem for this profile_id to get columns and indicators
    item = db.session.query(ScreenerProfileItem).filter_by(profile_id=profile_id).first()
    if not item:
        return jsonify({'selected_columns': [], 'indicators': []})

    return jsonify({
        'selected_columns': item.selected_columns or [],
        'indicators': item.indicators or []
    })

@screener_bp.route('/api/delete_profile/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    try:
        db.session.query(ScreenerProfileItem).filter_by(profile_id=profile_id).delete()
        db.session.query(ScreenerProfile).filter_by(profile_id=profile_id).delete()
        db.session.commit()
        return jsonify({'message': 'Profile deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


