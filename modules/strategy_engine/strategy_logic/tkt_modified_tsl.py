import datetime
import os
import json
import psycopg2
import pandas as pd

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

class TrailingStopLoss:
    def __init__(self, buy_price):
        self.buy_price = buy_price
        self.highest_price = buy_price
        self.stop_loss = buy_price * (1 + STOPLOSS_RULES[0]["stop"] / 100)

    def update(self, current_high, current_price):
        # Update highest price seen
        if current_high > self.highest_price:
            self.highest_price = current_high

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
        if new_stop_loss > self.stop_loss:
            self.stop_loss = new_stop_loss

        # Check sell condition
        sell_signal = current_price < self.stop_loss
        return sell_signal, self.stop_loss, gain


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
os.makedirs("logs", exist_ok=True)

def run(symbol, tick, indicators, market_is_open=True):
    if not market_is_open:
        print("Market is closed, skipping strategy execution.")
        return
    
    current_price = float(tick["last_trade_price"])
    current_high = float(tick.get("high_price", current_price))  # ensure high price is present

    # === If position exists, check for SELL ===
    if symbol in positions:
        tsl = positions[symbol]
        sell, stop_loss, gain = tsl.update(current_high, current_price)
        if sell:
            signal = {
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
            del positions[symbol]
        print(f"Position exists for {symbol}, current stop-loss: {tsl.stop_loss}, highest price: {tsl.highest_price}, gain: {gain:.2f}%")
        return

    # === BUY Logic ===
    if symbol not in historical_data:
        print(f"❌ No historical data available for {symbol}. Skipping BUY logic.")
        return
    
    last_day = historical_data[symbol]
    print("last day: ",last_day)
    
    close_today = float(tick["close_price"]) if "close_price" in tick else current_price
    sma = float(indicators.get("SMA-200-D", 0))
    rsi_val = float(indicators.get("RSI-14-D", 0))
    
    cond1 = rsi_val >= 60 and last_day["rsi"] >= 60
    cond2 = close_today > sma
    cond3 = current_price > last_day["high"]
    
    if cond1 and cond2 and cond3:
        signal = {
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
        positions[symbol] = TrailingStopLoss(current_price)  # start tracking stop-loss

    else:
        log_signal(f"❌ Conditions not met for {symbol}: RSI={rsi_val}, SMA={sma}, Close={close_today}, yesterday high={last_day['high']}, time={tick['timestamp']}")
        
        

def log_signal(signal):
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(signal) + "\n")
        print("logged: ", signal)
