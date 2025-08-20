import datetime
import pytz

from sqlalchemy import Column, Integer, Float, String, DateTime
from modules.db import Base, SessionLocal

class MarketData(Base):
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True)
    record_identifier = Column(String)
    symbol_code = Column(String)
    market_code = Column(String)
    symbol_state = Column(String)
    symbol_flag = Column(String)
    bid_volume = Column(Integer)
    bid_price = Column(Float)
    ask_price = Column(Float)
    ask_volume = Column(Integer)
    last_trade_price = Column(Float)
    last_trade_volume = Column(Integer)
    last_trade_time = Column(String)
    last_day_close_price = Column(Float)
    symbol_direction = Column(String)
    average_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    net_change = Column(Float)
    total_traded_volume = Column(Integer)
    total_trades = Column(Integer)
    open_price = Column(Float)
    timestamp = Column(DateTime)

FEED_FIELDS = [
    "record_identifier", "symbol_code", "market_code", "symbol_state", "symbol_flag",
    "bid_volume", "bid_price", "ask_price", "ask_volume", "last_trade_price",
    "last_trade_volume", "last_trade_time", "last_day_close_price", "symbol_direction",
    "average_price", "high_price", "low_price", "net_change", "total_traded_volume",
    "total_trades", "open_price"
]

def parse_numeric(value):
    if value == '':
        return None
    try:
        return float(value) if '.' in value else int(value)
    except ValueError:
        return None

def parse_feed(raw_feed):
    initial_values = raw_feed.split("|")
    if initial_values[0] != "FEED":
        return None

    additional_values = initial_values[1].split(";")
    values = initial_values[:1] + additional_values

    feed = {
        field: parse_numeric(values[i]) if field not in ["record_identifier", "symbol_code", "market_code", "symbol_state", "symbol_flag"] else values[i]
        for i, field in enumerate(FEED_FIELDS)
    }

    pkt_tz = pytz.timezone('Asia/Karachi')
    feed["timestamp"] = datetime.datetime.now(pkt_tz)

    return feed

def insert_feed_data(feed_data):
    session = SessionLocal()
    try:
        market_data = MarketData(
            record_identifier=feed_data.get("record_identifier"),
            symbol_code=feed_data.get("symbol_code"),
            market_code=feed_data.get("market_code"),
            symbol_state=feed_data.get("symbol_state"),
            symbol_flag=feed_data.get("symbol_flag"),
            bid_volume=feed_data.get("bid_volume"),
            bid_price=feed_data.get("bid_price"),
            ask_price=feed_data.get("ask_price"),
            ask_volume=feed_data.get("ask_volume"),
            last_trade_price=feed_data.get("last_trade_price"),
            last_trade_volume=feed_data.get("last_trade_volume"),
            last_trade_time=feed_data.get("last_trade_time"),
            last_day_close_price=feed_data.get("last_day_close_price"),
            symbol_direction=feed_data.get("symbol_direction"),
            average_price=feed_data.get("average_price"),
            high_price=feed_data.get("high_price"),
            low_price=feed_data.get("low_price"),
            net_change=feed_data.get("net_change"),
            total_traded_volume=feed_data.get("total_traded_volume"),
            total_trades=feed_data.get("total_trades"),
            open_price=feed_data.get("open_price"),
            timestamp=feed_data.get("timestamp")
        )

        session.add(market_data)
        session.commit()
        print("✅ Data inserted successfully")
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        session.rollback()
    finally:
        session.close()













# import datetime
# import pytz
# import psycopg2
# from sqlalchemy import Column, Integer, Float, String, DateTime
# # from flask_sqlalchemy import SQLAlchemy
# from modules.db import Base, SessionLocal


# class MarketData(Base):
#     __tablename__ = 'market_data'
#     id = db.Column(db.Integer, primary_key=True)
#     record_identifier = db.Column(db.String)
#     symbol_code = db.Column(db.String)
#     market_code = db.Column(db.String)
#     symbol_state = db.Column(db.String)
#     symbol_flag = db.Column(db.String)
#     bid_volume = db.Column(db.Integer)
#     bid_price = db.Column(db.Float)
#     ask_price = db.Column(db.Float)
#     ask_volume = db.Column(db.Integer)
#     last_trade_price = db.Column(db.Float)
#     last_trade_volume = db.Column(db.Integer)
#     last_trade_time = db.Column(db.String)
#     last_day_close_price = db.Column(db.Float)
#     symbol_direction = db.Column(db.String)
#     average_price = db.Column(db.Float)
#     high_price = db.Column(db.Float)
#     low_price = db.Column(db.Float)
#     net_change = db.Column(db.Float)
#     total_traded_volume = db.Column(db.Integer)
#     total_trades = db.Column(db.Integer)
#     open_price = db.Column(db.Float)
#     timestamp = db.Column(db.DateTime)

# FEED_FIELDS = [
#    "record_identifier", "symbol_code", "market_code", "symbol_state", "symbol_flag",
#     "bid_volume", "bid_price", "ask_price", "ask_volume", "last_trade_price",
#     "last_trade_volume", "last_trade_time", "last_day_close_price", "symbol_direction",
#     "average_price", "high_price", "low_price", "net_change", "total_traded_volume",
#     "total_trades", "open_price"
# ]



# def parse_numeric(value):
#     if value == '':
#         return None
#     try:
#         return float(value) if '.' in value else int(value  )
#     except ValueError:
#         return None

# def parse_feed(raw_feed):
#     initial_values = raw_feed.split("|")
#     if initial_values[0] != "FEED":
#         return None

#     additional_values = initial_values[1].split(";")
#     values = initial_values[:1] + additional_values

#     feed = {
#         field: parse_numeric(values[i]) if field not in ["record_identifier", "symbol_code", "market_code", "symbol_state", "symbol_flag",] else values[i]
#         for i, field in enumerate(FEED_FIELDS)
#     }

#     pkt_tz = pytz.timezone('Asia/Karachi')
#     feed["timestamp"] = datetime.datetime.now(pkt_tz).strftime('%Y-%m-%d %H:%M:%S')

#     return feed

# parse_feed("FEED|UBLPETF;REG;E0;;0;0;0;0;25;500;16:18:37;25.43;-;25.08;25.17;25;-.43;7500;11;25.17;|*")





# def insert_feed_data(feed_data):
#     try:
#         market_data = MarketData(
#             record_identifier=feed_data.get("record_identifier"),
#             symbol_code=feed_data.get("symbol_code"),
#             market_code=feed_data.get("market_code"),
#             symbol_state=feed_data.get("symbol_state"),
#             symbol_flag=feed_data.get("symbol_flag"),
#             bid_volume=feed_data.get("bid_volume"),
#             bid_price=feed_data.get("bid_price"),
#             ask_price=feed_data.get("ask_price"),
#             ask_volume=feed_data.get("ask_volume"),
#             last_trade_price=feed_data.get("last_trade_price"),
#             last_trade_volume=feed_data.get("last_trade_volume"),
#             last_trade_time=feed_data.get("last_trade_time"),
#             last_day_close_price=feed_data.get("last_day_close_price"),
#             symbol_direction=feed_data.get("symbol_direction"),
#             average_price=feed_data.get("average_price"),
#             high_price=feed_data.get("high_price"),
#             low_price=feed_data.get("low_price"),
#             net_change=feed_data.get("net_change"),
#             total_traded_volume=feed_data.get("total_traded_volume"),
#             total_trades=feed_data.get("total_trades"),
#             open_price=feed_data.get("open_price"),
#             timestamp=datetime.datetime.now()
#         )

#         db.session.add(market_data)
#         db.session.commit()
#         print("✅ Data inserted successfully")
#     except Exception as e:
#         print(f"❌ Error inserting data: {e}")
#         db.session.rollback()



