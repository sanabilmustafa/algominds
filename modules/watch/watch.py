from flask import render_template , jsonify , request
from . import watch_bp, db
from ..screener.screener import Stock

class Watch(db.Model):
    __tablename__ = "watch"

    watch_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)


class WatchProfile(db.Model):
    __tablename__ = "watch_profile"

    profile_id = db.Column(db.Integer, primary_key=True)
    watch_id = db.Column(db.Integer, db.ForeignKey("watch.watch_id", ondelete="CASCADE"),nullable=False)
    profile_name = db.Column(db.String, nullable=False)
    filters = db.Column(db.JSON)
    created_at = db.Column(db.DateTime,server_default=db.func.now() )
    is_default = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint(
            "watch_id",
            "is_default",
            name="unique_default_profile_per_watch"
        ),
    )

    # Relationships
    watch = db.relationship("Watch", backref=db.backref("profiles", cascade="all, delete-orphan"))

class WatchProfileItems(db.Model):
    __tablename__ = "watch_profile_items"

    item_id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer,db.ForeignKey("watch_profile.profile_id", ondelete="CASCADE"),nullable=False)
    stock_id = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime,server_default=db.func.now()
    )
    selected_columns = db.Column(db.JSON)
    __table_args__ = (
        db.UniqueConstraint("profile_id", "stock_id", name="unique_profile_stock"),
    )
    # Relationships
    profile = db.relationship("WatchProfile", backref=db.backref("items", cascade="all, delete-orphan"))

@watch_bp.route('/')
def watch_home():
    return render_template('watch.html')


@watch_bp.route('/api/stocks/symbols')
def get_symbols():
    try:
        symbols = db.session.query(Stock.stock_id, Stock.symbol).distinct().order_by(Stock.symbol).all()
        return jsonify([{"id": row[0], "symbol": row[1]} for row in symbols])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Create WatchList Function
@watch_bp.route("/api/watchlist", methods=["POST"])
def create_watchlist():
    data = request.get_json()
    try:
        profile = WatchProfile(
            watch_id=data["watch_id"],
            profile_name=data["profile_name"],
            is_default=data.get("is_default", False)
        )
        db.session.add(profile)
        db.session.flush()  # get profile_id before commit

        # 2. Add WatchProfileItems
        for stock in data["stocks"]:
            item = WatchProfileItems(
                profile_id=profile.profile_id,
                stock_id=stock["id"],
                selected_columns=stock["columns"]
            )
            db.session.add(item)

        db.session.commit()

        return jsonify({"success": True, "profile_id": profile.profile_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    


# Get All the profiles
@watch_bp.route("/api/watchlist/profiles", methods=["GET"])
def get_watch_profiles():
    try:
        profiles = db.session.query(WatchProfile).all()
        return jsonify([
            {
                "id": p.profile_id,
                "profile_name": p.profile_name,
                "is_default": p.is_default
            }
            for p in profiles
        ])
        print(profiles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@watch_bp.route("/api/watchlist/profiles/<int:profile_id>", methods=["GET"])
def get_single_watch_profile(profile_id):
    try:
        profile = WatchProfile.query.get_or_404(profile_id)
        return jsonify({
            "id": profile.profile_id,
            "profile_name": profile.profile_name,
            "is_default": profile.is_default,
            "stocks": [item.stock_id for item in profile.items],
            "columns": list({col for item in profile.items for col in item.selected_columns})
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@watch_bp.route("/api/watchlist/profiles/<int:profile_id>", methods=["PUT"])
def update_watch_profile(profile_id):
    data = request.get_json()
    try:
        profile = WatchProfile.query.get_or_404(profile_id)
        profile.profile_name = data.get("profile_name", profile.profile_name)
        profile.is_default = data.get("is_default", profile.is_default)

        new_columns = set()
        if "columns" in data:
            new_columns = set(data["columns"])
            existing_items = WatchProfileItems.query.filter_by(profile_id=profile_id).all()
            for item in existing_items:
                old_cols = set(item.selected_columns or [])
                item.selected_columns = list(old_cols.union(new_columns))

        # Get full set of columns from any existing stock in the profile
        all_existing_columns = set()
        for item in profile.items:
            all_existing_columns.update(item.selected_columns or [])

        # Handle stock additions
        if "stocks" in data:
            existing_stock_ids = {item.stock_id for item in profile.items}
            new_stock_ids = set(int(s) for s in data["stocks"]) - existing_stock_ids

            for stock_id in new_stock_ids:
                db.session.add(WatchProfileItems(
                    profile_id=profile_id,
                    stock_id=stock_id,
                    # Give new stock all current columns from profile, plus any new ones sent
                    selected_columns=list(all_existing_columns.union(new_columns))
                ))

        db.session.commit()
        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@watch_bp.route("/api/watchlist/profiles/<int:profile_id>", methods=["DELETE"])
def delete_watch_profile(profile_id):
    try:
        profile = WatchProfile.query.get_or_404(profile_id)
        db.session.delete(profile)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
