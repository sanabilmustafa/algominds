import datetime
import os
import json
import psycopg2
import pandas as pd
from psycopg2.extras import Json
from modules.order.order import send_order
# import sys
# sys.path.append('/Users/rubasmustafa/Desktop/Analytics/algominds-app-compilation/modules/order')
# from order import send_order

# === TRAILING STOPLOSS CONFIG ===
STOPLOSS_RULES = [
    {"gain": 0,   "stop": -6},   # Initial stop-loss: -6% from buy  
    {"gain": 5,   "stop": -2},
    {"gain": 8,   "stop": 0},
    {"gain": 12,  "stop": 4},
    {"gain": 16,  "stop": 8},
    {"gain": 20,  "stop": 10},
    {"gain": 25,  "stop": 15},
]
AFTER_STEP = 5     # Every +5% gain after 25%
AFTER_DIFF = 10    # Stop-loss = High - 10% of High

# Tracks open positions with stop-loss state
positions = {}

def get_db_connection():
    # reuse credentials you already used in prepare_strategy_data
    return psycopg2.connect(
        host="localhost",
        dbname="AlgoMinds",
        user="algominds",
        password="machinedatabase"
    )
    
class TrailingStopLoss:
    def __init__(self, buy_price, highest_price=None, stop_loss=None):
        self.buy_price = float(buy_price)
        self.highest_price = float(highest_price) if highest_price is not None else float(buy_price)
        # default initial stop_loss if not provided
        if stop_loss is None:
            self.stop_loss = self.buy_price * (1 + STOPLOSS_RULES[0]["stop"] / 100)
        else:
            self.stop_loss = float(stop_loss)

    def to_dict(self):
        return {
            "buy_price": self.buy_price,
            "highest_price": self.highest_price,
            "stop_loss": self.stop_loss
        }

    @staticmethod
    def from_dict(d):
        return TrailingStopLoss(d["buy_price"], highest_price=d.get("highest_price"), stop_loss=d.get("stop_loss"))


    def update(self, current_high, current_price):
        # Update highest price seen
        if current_high > self.highest_price:
            self.highest_price = float(current_high)

        gain = ((self.highest_price - self.buy_price) / self.buy_price) * 100
        new_stop_loss = self.stop_loss

        # Check standard rules first
        for rule in STOPLOSS_RULES:
            if gain >= rule["gain"]:
                candidate = self.buy_price * (1 + rule["stop"] / 100)
                if candidate > new_stop_loss:
                    new_stop_loss = candidate

        # After max threshold, apply step rule
        if gain > STOPLOSS_RULES[-1]["gain"]:
            extra_gain = gain - STOPLOSS_RULES[-1]["gain"]
            steps = int(extra_gain // AFTER_STEP)
            if steps > 0:
                trailing_stop = self.highest_price * (1 - AFTER_DIFF / 100)
                if trailing_stop > new_stop_loss:
                    new_stop_loss = trailing_stop

        # Update stop-loss only if it moves higher
        moved = False
        if new_stop_loss > self.stop_loss:
            self.stop_loss = new_stop_loss
            moved = True

        sell_signal = current_price < self.stop_loss
        return sell_signal, self.stop_loss, gain, moved

# --- DB helpers for positions persistence ---
def init_positions_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            symbol TEXT PRIMARY KEY,
            buy_price DOUBLE PRECISION NOT NULL,
            highest_price DOUBLE PRECISION NOT NULL,
            stop_loss DOUBLE PRECISION NOT NULL,
            opened_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            meta JSONB DEFAULT '{}'::jsonb
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
def save_position_to_db(symbol, tsl: TrailingStopLoss, meta=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO positions (symbol, buy_price, highest_price, stop_loss, meta)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (symbol) DO UPDATE
          SET buy_price = EXCLUDED.buy_price,
              highest_price = EXCLUDED.highest_price,
              stop_loss = EXCLUDED.stop_loss,
              meta = EXCLUDED.meta;
    """, (symbol, tsl.buy_price, tsl.highest_price, tsl.stop_loss, Json(meta or {})))
    conn.commit()
    cur.close()
    conn.close()

def remove_position_from_db(symbol):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM positions WHERE symbol = %s;", (symbol,))
    conn.commit()
    cur.close()
    conn.close()

def load_positions_from_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT symbol, buy_price, highest_price, stop_loss, meta FROM positions;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    loaded = {}
    for symbol, buy_price, highest_price, stop_loss, meta in rows:
        tsl = TrailingStopLoss(buy_price, highest_price=highest_price, stop_loss=stop_loss)
        loaded[symbol] = tsl
    return loaded

# --- Initialize and load on startup ---
init_positions_table()
positions = load_positions_from_db()  # override previous in-memory dict on startup

def rsi(bars, period=14):
    """
    Calculates the Relative Strength Index (RSI) using Wilder's Smoothing.
    This is the standard method used on platforms like TradingView.
    """

    prices = [bar["close"] for bar in bars]
    if len(prices) <= period:
        return [None] * len(prices)
    
    delta = pd.Series(prices).diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Use Exponential Moving Average for smoothing gains and losses
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    with open("rsi.txt", "w") as f:
        json.dump(rsi.tolist(), f)
    return rsi.tolist()

def fetch_historical_bars(conn, days=30):
    cursor = conn.cursor()
    # start_date = '2025-01-01'
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days + 1)
    print("Fetching historical bars from:", start_date)
    query = """
        SELECT symbol, date, close
        FROM historical
        WHERE date >= %s
        ORDER BY symbol, date
    """
    cursor.execute(query, (start_date,))
    rows = cursor.fetchall()
    data = {}
    for symbol, date, close in rows:
        if symbol not in data:
            data[symbol] = []
        data[symbol].append({"date": date, "close": float(close)})
    return data 

def calculate_rsi_for_all(historical_bars):
    symbol_to_rsi = {}
    for symbol, bars in historical_bars.items():
        rsi_list = rsi(bars)
        if len(rsi_list) > 1 and rsi_list[-2] is not None:
            symbol_to_rsi[symbol] = round(rsi_list[-2], 2)
    # log_signal(f"Calculated RSI for {symbol_to_rsi} symbols.")
    return symbol_to_rsi

def fetch_last_day_price_info(conn):
    cursor = conn.cursor()
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    # weekday(): Monday=0, Sunday=6
    if yesterday.weekday() == 6:  # Sunday
        yesterday = yesterday - datetime.timedelta(days=2)  # Go to Friday
    elif yesterday.weekday() == 5:  # Saturday
        yesterday = yesterday - datetime.timedelta(days=1)  # Go to Friday
    else:
        yesterday = today - datetime.timedelta(days=2)
    # yesterday = '2025-01-01'
    query = """
        SELECT symbol, high, close
        FROM historical
        WHERE date = %s
    """
    cursor.execute(query, (yesterday,))
    rows = cursor.fetchall()
    price_data = {}
    for symbol, high, close in rows:
        price_data[symbol] = {
            "high": float(high),
            "close": float(close)
        }
    return price_data

def prepare_strategy_data():
    conn = psycopg2.connect(
        host="localhost",
        dbname="AlgoMinds",
        user="algominds",
        password="machinedatabase"
    )
    historical_bars = fetch_historical_bars(conn)
    rsi_values = calculate_rsi_for_all(historical_bars)
    price_info = fetch_last_day_price_info(conn)
    historical_data = {}
    for symbol in price_info:
        if symbol in rsi_values:
            historical_data[symbol] = {
                "high": price_info[symbol]["high"],
                "close": price_info[symbol]["close"],
                "rsi": rsi_values[symbol]
            }
    conn.close()
    return historical_data

historical_data = prepare_strategy_data()

today_str = datetime.date.today().isoformat()
LOG_PATH = os.path.join("logs", f"tkt_modified_{today_str}.log")
# os.makedirs("logs", exist_ok=True)
# --- Modify run() logic slightly to persist on BUY, stop update, SELL ---
def run(symbol, tick, indicators, market_is_open=True):
    if not market_is_open:
        print("Market is closed, skipping strategy execution.")
        return
    
    if tick["last_trade_price"] is not None:
        current_price = float(tick["last_trade_price"])
        current_high = float(tick.get("high_price", current_price))
    else:
        print(f"No last trade price available for {symbol}. Skipping.")
        return
    # If position exists, check for SELL
    if symbol in positions:
        tsl = positions[symbol]
        sell, stop_loss, gain, moved = tsl.update(current_high, current_price)
        if moved:
            # persist stop-loss update
            save_position_to_db(symbol, tsl)
        if sell:
            signal = {
                "strategy": "TKT modified TSL",
                "symbol": symbol,
                "signal": "SELL",
                "price": current_price,
                "timestamp": tick["timestamp"],
                "reason": {
                    "stop_loss_triggered": True,
                    "stop_loss": stop_loss,
                    "gain_since_buy": gain
                }
            }
            log_signal(signal)
            send_order("TEST05", 1111, 1, current_price, symbol, 2, 1, "222", "0.0", "01") 
            log_signal(f"tkt modified tsl: SELL order sent for {symbol} at price {current_price}, gain: {gain:.2f}%")
            
            del positions[symbol]
            remove_position_from_db(symbol)
        print(f"tkt Modified tsl: Position exists for {symbol}, stop-loss: {tsl.stop_loss}, highest: {tsl.highest_price}, gain: {gain:.2f}%")
        return

    # BUY logic (unchanged except that we persist)
    if symbol not in historical_data:
        print(f"No historical data available for {symbol}. Skipping BUY logic.")
        return

    last_day = historical_data[symbol]

    # close_today = float(tick["close_price"]) if "close_price" in tick else current_price
    close_today = current_price
    sma200 = float(indicators.get("SMA-200-D", 0))
    sma45 = float(indicators.get("SMA-45-D", 0))
    rsi_val = float(indicators.get("RSI-14-D", 0))

    cond1 = rsi_val >= 60
    cond2 = close_today > sma200
    cond3 = current_price > last_day["high"]
    cond4 = close_today > sma45
    if symbol == 'INIL':
        if cond1:
            print("condition 1 true for ", symbol)
        else:
            print(rsi_val, last_day["rsi"])
        if cond2:
            print("condition 2 true for ", symbol)
        if cond3:
            print("condition 3 true for ", symbol)
        if cond4:
            print("condition 4 true for ", symbol)

    if cond1 and cond2 and cond3 and cond4:
        signal = {
            "strategy": "TKT modified TSL",
            "symbol": symbol,
            "signal": "BUY",
            "price": current_price,
            "timestamp": tick["timestamp"],
            "reason": {
                "rsi_today": rsi_val,
                "rsi_yesterday": last_day["rsi"],
                "close_gt_sma": cond2,
                "price_gt_prev_high": cond3
            }
        }
        log_signal(signal)
        send_order("TEST05", 1111, 1, current_price, symbol, 1, 1,"222", "0.0", "01") 
        log_signal(f"tkt modified tsl: BUY order sent for {symbol} at price {current_price}, RSI={rsi_val}, SMA-200={sma200}, Close={close_today}, yesterday high={last_day['high']}")

        tsl = TrailingStopLoss(current_price)
        positions[symbol] = tsl
        save_position_to_db(symbol, tsl, meta={"reason": "entry_conditions_passed"})
    else:
        log_signal(f"tkt modified tsl: Conditions not met for {symbol}: RSI={rsi_val}, SMA={sma200}, Close={close_today}, yesterday high={last_day['high']}, time={tick['timestamp']}")

def log_signal(signal):
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(signal) + "\n")
        print("logged: ", signal)
