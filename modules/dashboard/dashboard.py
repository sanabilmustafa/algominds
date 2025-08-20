from flask import  jsonify, request, render_template, current_app , app
from . import dashboard_bp , db  # import your dashboard blueprint if needed
import requests
from sqlalchemy import text



@dashboard_bp.route('/')
def dashboard_home():
    client_id = request.args.get('client_id', 1)  # or fetch from session/user auth

    # Construct the API endpoint URL
    current_app.config['API_BASE_URL'] = "http://127.0.0.1:8000/strategy"
    api_url = f"{current_app.config['API_BASE_URL']}/strategies"
    params = {
        "client_id": client_id,
        "deploy_status": "Deployed"
    }

    try:
        # Call the API
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        strategies = response.json()  # Expecting API returns JSON
    except requests.RequestException as e:
        strategies = []
        print(f"Error fetching strategies: {e}")
    print(strategies)
    return render_template('dashboard.html', strategies=strategies['strategies'])
from sqlalchemy import text

@dashboard_bp.route("/api/save_watchlist", methods=["POST"])
def save_watchlist():
    try:
        data = request.get_json()
        symbols = data.get("symbols", [])
        user_id = 1  # Replace with current user id

        if not symbols:
            return jsonify({"error": "No symbols provided"}), 400

        # Fetch stock_ids for given symbols
        result = db.session.execute(
            text("SELECT stock_id FROM stock WHERE symbol IN :symbols"),
            {"symbols": tuple(symbols)}
        ).fetchall()
        stock_ids = [row[0] for row in result]

        # Clear old watchlist
        db.session.execute(
            text("DELETE FROM dashboard_watchlist WHERE user_id = :uid"),
            {"uid": user_id}
        )

        # Insert new watchlist entries
        for sid in stock_ids:
            db.session.execute(
                text("INSERT INTO dashboard_watchlist (stock_id, user_id) VALUES (:sid, :uid)"),
                {"sid": sid, "uid": user_id}
            )

        db.session.commit()
        return jsonify({"message": "Watchlist updated"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/get_watchlist", methods=["GET"])
def get_watchlist():
    try:
        user_id = 1  # TODO: Replace with current logged-in user

        query = text("""
            SELECT 
                s.symbol,
                md.last_trade_price AS price,
                md.net_change AS change
            FROM dashboard_watchlist dw
            JOIN stock s ON dw.stock_id = s.stock_id
            JOIN market_data md 
                ON s.symbol = md.symbol_code
            WHERE dw.user_id = :uid
            AND md.timestamp = (
                SELECT MAX(md2.timestamp)
                FROM market_data md2
                WHERE md2.symbol_code = s.symbol
                    AND md2.last_trade_price IS NOT NULL
            )
        """)


        rows = db.session.execute(query, {"uid": user_id}).mappings().all()

        watchlist_data = [
            {
                "symbol": row["symbol"],
                "price": float(row["price"]) if row["price"] is not None else None,
                "change": float(row["change"]) if row["change"] is not None else None
            }
            for row in rows
        ]
        print("now we are printin teh adat ")
        print(watchlist_data)
        return jsonify({"watchlist": watchlist_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
