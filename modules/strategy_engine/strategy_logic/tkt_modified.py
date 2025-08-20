# strategy_logic/tkt_modified.py

import datetime
import os
import json
# from modules.indicators.calculator import rsi  # Import RSI calculation function
import psycopg2
import pandas as pd

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
    today = datetime.date.today()
    # start_date = today - datetime.timedelta(days=days + 1)
    start_date = '2025-01-01'
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
    print("fetch historical bar: ",data)
    return data 

def calculate_rsi_for_all(historical_bars):
    symbol_to_rsi = {}

    for symbol, bars in historical_bars.items():
        rsi_list = rsi(bars)
        if len(rsi_list) > 1 and rsi_list[-2] is not None:  # -2 is yesterday's RSI
            symbol_to_rsi[symbol] = round(rsi_list[-2], 2)
    print("Calculated RSI values for symbols:", symbol_to_rsi)
    return symbol_to_rsi  # Example: {"BOP": 62.5}

def fetch_last_day_price_info(conn):
    cursor = conn.cursor()
    # yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = '2025-01-01'

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
    print("Last day price info:", price_data)
    return price_data


def prepare_strategy_data():
    print("Preparing strategy data...")
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

# Set up log path
today_str = datetime.date.today().isoformat()
LOG_PATH = os.path.join("logs", f"tkt_modified_{today_str}.log")
os.makedirs("logs", exist_ok=True)

def run(symbol, tick, indicators, market_is_open=True):
    print("Running TKT modified strategy for", symbol)
    """Evaluates the buy condition for a given symbol tick and indicator data."""

    if not market_is_open:
        print("return Market is closed, no signal generated.")
        return  # Market closed — no signal
    
    # Ensure we have historical data
    if symbol not in historical_data:
        print("returning no symbol in historical data ")
        return
    
    last_day = historical_data[symbol]
    
    # Extract real-time values
    current_price = float(tick["last_trade_price"])
    close_today = float(tick["close_price"]) if "close_price" in tick else current_price
    sma = float(indicators.get("sma", 0))
    rsi = float(indicators.get("rsi", 0))
    
    # Strategy conditions
    cond1 = rsi >= 60 and last_day["rsi"] >= 60
    cond2 = close_today > sma
    cond3 = current_price > last_day["high"]
    
    print(cond1, cond2, cond3)
    if cond1 and cond2 and cond3:
        signal = {
            "symbol": symbol,
            "signal": "BUY",
            "price": current_price,
            "timestamp": tick["timestamp"],
            "reason": {
                "rsi_today": rsi,
                "rsi_yesterday": last_day["rsi"],
                "close_gt_sma": cond2,
                "price_gt_prev_high": cond3
            }
        }
        log_signal(signal)
    else:
        print("❌ No signal generated for", symbol)

def log_signal(signal):
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(signal) + "\n")
    print("✅ Signal logged:", signal)
