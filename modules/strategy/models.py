from modules.database import db
from datetime import datetime

class Strategy(db.Model):
    __tablename__ = 'strategies'

    strategy_id = db.Column(db.Integer, primary_key=True)
    strategy_author = db.Column(db.String(255), nullable=False, default='AlgoMinds')
    client_id = db.Column(db.Integer, nullable=False)
    strategy_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('Active', 'Inactive', 'Testing', name='strategy_status_enum'), default='Inactive')
    deploy_status = db.Column(db.Enum('Deployed', 'Undeployed', name='deploy_status_enum'), default='Undeployed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    allow_update = db.Column(db.Boolean, default=True)

    # stocks = db.Column(ARRAY(db.String))  # PostgreSQL ARRAY type
    allocation_of_assets = db.Column(db.Integer)  # 1-100, validate in Python

class StrategyStocks(db.Model):
    __tablename__ = 'strategy_stock_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.strategy_id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    allocation_percent = db.Column(db.Integer, nullable=False)  # Percentage allocation for the stock


# class Historical(db.Model):
#     __tablename__ = 'historical'

#     id = db.Column(db.Integer, primary_key=True)
#     stock_symbol = db.Column(db.String)
#     date = db.Column(db.Date)
#     open = db.Column(db.Float)
#     high = db.Column(db.Float)
#     low = db.Column(db.Float)
#     close = db.Column(db.Float)
#     volume = db.Column(db.Float)
    
# Define the Historical Model
class Historical(db.Model):
    """
    Represents the 'historical' table in the database.
    Stores historical stock data.
    """
    __tablename__ = 'historical'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    open = db.Column(db.Numeric(10,2), nullable=False)
    high = db.Column(db.Numeric(10,2), nullable=False)
    low = db.Column(db.Numeric(10,2), nullable=False)
    close = db.Column(db.Numeric(10,2), nullable=False)
    volume = db.Column(db.Numeric(10,2), nullable=False)
    symbol = db.Column(db.String(50), nullable=True)
    


class MarketData(db.Model):
    """
    Represents the 'market_data' table in the database.
    Stores real-time or daily market data for various symbols.
    """
    __tablename__ = 'market_data'

    # Primary Key
    market_data_id = db.Column(db.Integer, primary_key=True)

    # Symbol and Market Information
    record_identifier = db.Column(db.String(10), nullable=True)
    symbol_code = db.Column(db.String(50), nullable=True)
    market_code = db.Column(db.String(10), nullable=True)
    symbol_state = db.Column(db.String(10), nullable=True)
    symbol_flag = db.Column(db.String(10), nullable=True)
    symbol_direction = db.Column(db.String(10), nullable=True)

    # Bid and Ask Prices/Volumes
    bid_volume = db.Column(db.Numeric, nullable=True)
    bid_price = db.Column(db.Numeric, nullable=True)
    ask_price = db.Column(db.Numeric, nullable=True)
    ask_volume = db.Column(db.Numeric, nullable=True)

    # Trade Information
    last_trade_price = db.Column(db.Numeric, nullable=True)
    last_trade_volume = db.Column(db.Numeric, nullable=True)
    last_trade_time = db.Column(db.String(10), nullable=True) # Using String as per schema, consider Time type if format is consistent
    total_traded_volume = db.Column(db.Numeric, nullable=True)
    total_trades = db.Column(db.Numeric, nullable=True)

    # Price Statistics
    last_day_close_price = db.Column(db.Numeric, nullable=True)
    average_price = db.Column(db.Numeric, nullable=True)
    high_price = db.Column(db.Numeric, nullable=True)
    low_price = db.Column(db.Numeric, nullable=True)
    open_price = db.Column(db.Numeric, nullable=True)
    net_change = db.Column(db.Numeric, nullable=True)

    # Timestamp
    timestamp = db.Column(db.DateTime, nullable=True)

    
# class Position(db.Model):
#     __tablename__ = 'positions'

#     id = db.Column(db.Integer, primary_key=True)
#     symbol =db.Column(db.String, nullable=False)
#     strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.strategy_id', ondelete='CASCADE'), nullable=False)
#     buy_price = db.Column(db.Float, nullable=False)
#     stop_loss = db.Column(db.Float, nullable=False)
#     current_high = db.Column(db.Float, nullable=False)
#     state = db.Column(db.Integer, default=0)
#     created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
#     updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now(), server_default=db.func.now())
