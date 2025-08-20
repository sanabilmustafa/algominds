import datetime
import os
import json
import psycopg2


test_positions = {}
total_profit = 0.0
total_loss = 0.0

today_str = datetime.date.today().isoformat()
LOG_PATH = os.path.join("logs", f"new_test_{today_str}.log")

def log_signal(signal):
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(signal) + "\n")
        print("logged: ", signal)


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
        yesterday = cursor.fetchone()[0]
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

def run(symbol, tick, indicators, market_is_open=True):
    conn = psycopg2.connect(
        host="localhost",
        dbname="AlgoMinds",
        user="algominds",
        password="machinedatabase"
    )
    global total_profit, total_loss
    if not market_is_open:
        return
    if tick['last_trade_price'] is None:
        print(f"[TEST] No last trade price for {symbol}, skipping...")
        return
    price = float(tick["last_trade_price"])
    rsi_val = float(indicators.get('RSI-14-D', 0))  # Use a longer RSI for more stable signals
    last_day_price_values = fetch_last_day_price_info(conn)
    last_day_high = last_day_price_values[symbol]["high"] if symbol in last_day_price_values else None
    
    if symbol in test_positions:
        buy_price = test_positions[symbol]["buy_price"]
        pnl = (price - buy_price) / buy_price * 100
        if pnl > 0:
            total_profit += pnl
        else:
            total_loss += abs(pnl)
        
        if price is None:
            return 

        sell_cond = (price < buy_price * 0.98) or (price > buy_price * 1.03) or (pnl > 3) or (pnl < -2)
        if sell_cond:
            signal = {
                "strategy_name": "test_strategy",
                "symbol": symbol,
                "signal": "SELL",
                "bought_price": buy_price,
                "sell price": price,
                "timestamp": tick["timestamp"],
                "pnl_percent": round(pnl, 2),
                "total_profit_percent": round(total_profit, 2),
                "total_loss_percent": round(total_loss, 2)
            }
            log_signal(signal)
            print(f"[TEST] SELL {symbol} at {price} | PnL: {pnl:.2f}% | Total Profit: {total_profit:.2f}% | Total Loss: {total_loss:.2f}%")
            del test_positions[symbol]
            return
    if(last_day_high is None) or rsi_val is None:
        print(f"[TEST] No last day high or rsi_val for {symbol}, skipping buy")
        return
    buy_cond =  50 < rsi_val < 65 and price > last_day_high
    if buy_cond:
        if symbol in test_positions:
            print(f"[TEST] Already holding {symbol}, skipping buy")
            return
        
        test_positions[symbol] = {
            "buy_price": price,
            "timestamp": tick["timestamp"]
        }
        signal = {
            "strategy_name": "test_strategy",
            "symbol": symbol,
            "signal": "BUY",
            "price": price,
            "rsi": rsi_val,
            "last_day_high": last_day_high,
            "timestamp": tick["timestamp"]
        }
        log_signal(signal)
        print(f"[TEST] BUY {symbol} at {price}")