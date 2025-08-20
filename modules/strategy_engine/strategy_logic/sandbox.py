import datetime
import os
import json

test_positions = {}
total_profit = 0.0

today_str = datetime.date.today().isoformat()
LOG_PATH = os.path.join("logs", f"sandbox_{today_str}.log")

def log_signal(signal):
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(signal) + "\n")
        print("logged: ", signal)

def run(symbol, tick, indicators, market_is_open=True):
    global total_profit
    if not market_is_open:
        return
    
    if tick['last_trade_price'] is None:
        print(f"[TEST] No last trade price for {symbol}, skipping...")
        return
        
    price = float(tick["last_trade_price"])
    sma_fast = float(indicators.get("SMA-2-D", 0))
    sma_slow = float(indicators.get("SMA-5-D", 0))
    rsi_val = float(indicators.get("RSI-3-D", 0))  # short RSI for quick flips

    # --- SELL LOGIC ---
    if symbol in test_positions:
        buy_price = test_positions[symbol]["buy_price"]
        pnl = (price - buy_price) / buy_price * 100

        sell_cond = (sma_fast < sma_slow) or (rsi_val > 60) or pnl > 1 or pnl < -0.5
        if sell_cond:
            total_profit += pnl
            signal = {
                "strategy_name": "Sandbox",
                "symbol": symbol,
                "signal": "SELL",
                "price": price,
                "timestamp": tick["timestamp"],
                "pnl_percent": round(pnl, 2),
                "total_profit_percent": round(total_profit, 2)
            }
            log_signal(signal)
            print(f"[TEST] SELL {symbol} at {price} | PnL: {pnl:.2f}% | Total PnL: {total_profit:.2f}%")
            del test_positions[symbol]
        return

    # --- BUY LOGIC ---
    buy_cond = (sma_fast > sma_slow) or (rsi_val < 40)
    if buy_cond:
        test_positions[symbol] = {
            "buy_price": price,
            "timestamp": tick["timestamp"]
        }
        signal = {
            "strategy_name": "Sandbox",
            "symbol": symbol,
            "signal": "BUY",
            "price": price,
            "timestamp": tick["timestamp"]
        }
        log_signal(signal)
        print(f"[TEST] BUY {symbol} at {price} | SMA2={sma_fast}, SMA5={sma_slow}, RSI3={rsi_val}")

    else:
        log_signal("No buy signal generated "+ f"for {symbol} at {price} | SMA2={sma_fast}, SMA5={sma_slow}, RSI3={rsi_val}")
