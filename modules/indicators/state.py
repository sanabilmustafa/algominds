import psycopg2
from psycopg2.extras import RealDictCursor
from collections import defaultdict
from datetime import datetime
import threading
import asyncio

# Cache structure: { symbol: [bar1, bar2, ..., barN] }
symbol_cache = defaultdict(list)
lock = threading.Lock()  # Safe updates across threads

# PostgreSQL config — change if needed
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "AlgoMinds",
    "user": "algominds",
    "password": "machinedatabase"
}

# -- Convert row to OHLC dict
def row_to_bar(row):
    return {
        "date": row["date"].strftime("%Y-%m-%d"),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "volume": float(row["volume"])
    }
db_lock = asyncio.Lock()

# -- Load last N bars from PostgreSQL for a given symbol
async def get_historical_bars(symbol, timeinterval="1d", limit=200):
    print(timeinterval)
    async with db_lock:
        if symbol in symbol_cache:
            return symbol_cache[symbol]

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            if timeinterval == "1d":
                query = """
                    SELECT date, open, high, low, close, volume
                    FROM historical
                    WHERE symbol = %s
                    ORDER BY date DESC
                    LIMIT %s
                """
                # query = """
                #  SELECT 
                #     candle_close_time AS date,
                #     open_price AS open, 
                #     high_price AS high, 
                #     low_price AS low, 
                #     close_price AS close, 
                #     volume
                # FROM ohlc_1d
                # WHERE symbol_code = %s
                # ORDER BY candle_close_time DESC
                # LIMIT %s;
                # """
            elif timeinterval == "1h":
                query = """
                    SELECT
                        candle_close_time AS date,
                        open_price AS open, 
                        high_price AS high, 
                        low_price AS low, 
                        close_price AS close, 
                        volume
                    FROM ohlc_1h
                    WHERE symbol_code = %s
                    ORDER BY candle_close_time DESC
                    LIMIT %s
                """
            elif timeinterval == "15min":
                query = """
                    SELECT
                        candle_close_time AS date,
                        open_price AS open, 
                        high_price AS high, 
                        low_price AS low, 
                        close_price AS close, 
                        volume
                    FROM ohlc_15min
                    WHERE symbol_code = %s
                    ORDER BY candle_close_time DESC
                    LIMIT %s
                """
            elif timeinterval == "30min":
                query = """
                    SELECT
                        candle_close_time AS date,
                        open_price AS open, 
                        high_price AS high, 
                        low_price AS low, 
                        close_price AS close, 
                        volume
                    FROM ohlc_30min
                    WHERE symbol_code = %s
                    ORDER BY candle_close_time DESC
                    LIMIT %s
                """
            elif timeinterval == "1w":
                query = """
                    SELECT
                        candle_close_time AS date,
                        open_price AS open, 
                        high_price AS high, 
                        low_price AS low, 
                        close_price AS close, 
                        volume
                    FROM ohlc_1w
                    WHERE symbol_code = %s
                    ORDER BY candle_close_time DESC
                    LIMIT %s
                """
            else:
                print("--------------> getting the historical data")
                query = """
                    SELECT date, open, high, low, close, volume
                    FROM historical
                    WHERE symbol = %s
                    ORDER BY date DESC
                    LIMIT %s
                """
                print(f"Unsupported time interval: {timeinterval}")
            cur.execute(query, (symbol, limit))
            rows = cur.fetchall()
            bars = [row_to_bar(row) for row in reversed(rows)]  # oldest first
            symbol_cache[symbol] = bars
            # print(f"bars for the historial: ", bars)
            return bars
        except Exception as e:
            print(f"Error fetching historical for {symbol}: {e}")
            return []
        finally:
            if conn:
                conn.close()

async def get_last_trade(symbol: str):
    async with db_lock:
        print("get last trade called")
        query = """
            SELECT *
            FROM market_data
            WHERE symbol_code = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, (symbol,))
            row = cur.fetchone()
            conn.close()
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"[ERROR] Fetching last trade for {symbol}: {e}")
            return None

    
    
# -- Update bar list with a new tick
def update_symbol_history(symbol, tick):
    """
    Append tick as new bar (OHLC format). Assumes tick has keys: open, high, low, close.
    Keeps last 100 bars only.
    """
    with lock:
        bar = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "open": tick["open_price"],
            "high": tick["high_price"],
            "low": tick["low_price"],
            "close": tick["last_trade_price"],
            "volume": tick.get("total_traded_volume", 0)
        }

        if symbol in symbol_cache:
            bars = symbol_cache[symbol]
            bars.append(bar)
            if len(bars) > 100:
                bars.pop(0)
        else:
            symbol_cache[symbol] = [bar]
        # print(symbol_cache[symbol])
        return symbol_cache[symbol]
    


#    CREATE TABLE ohlc_1d (
#     symbol_code TEXT NOT NULL,
#     candle_close_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
#     open_price NUMERIC(12,4),
#     high_price NUMERIC(12,4),
#     low_price NUMERIC(12,4),
#     close_price NUMERIC(12,4),
#     volume NUMERIC(20,2),
#     PRIMARY KEY (symbol_code, candle_close_time)
# );
# # Until you introduce Redis, use something like this in state.py:

# # # key: indicator+symbol; value: list of websocket clients
# # subscriptions = {
# #     "sma_20:HBL": [client1, client2],
# #     "rsi_14:OGDC": [client2]
# # }

# # # latest value cache (useful for immediately responding to new subscribers)
# # latest_values = {
# #     "sma_20:HBL": 42.15,
# #     "rsi_14:OGDC": 55.7
# # }
# # This lets you:

# # Only compute sma_20:HBL once, even if multiple clients want it.

# # Immediately respond to new subscriptions with the current value.

# # Avoid recomputation unless a new bar tick comes in.

# # 📘 FUNCTIONAL API DESIGN
# # 🔁 Cache Initialization
# # def initialize_symbol(symbol: str, timeframe: str) -> None
# # 📥 Update bar data
# # def append_bar(symbol: str, timeframe: str, bar: dict) -> None
# # 📤 Get bar data
# # def get_bars(symbol: str, timeframe: str) -> list
# # 🧮 Set indicator results
# # def set_indicator(symbol: str, timeframe: str, name: str, values: list) -> None
# # 📊 Get indicator results
# # def get_indicator(symbol: str, timeframe: str, name: str) -> list
# # 🧹 Reset / clear cache (if needed for debugging or reload)
# # def clear_cache() -> None



# # indicators/state.py

# from collections import defaultdict, deque

# # Maximum number of bars to keep in memory (can be adjusted)
# MAX_BARS = 200

# # The main cache object: {(symbol, timeframe): {bars: deque[], indicators: {}}}
# _cache = defaultdict(lambda: {
#     "bars": deque(maxlen=MAX_BARS),
#     "indicators": {}
# })

# # ---------------------------------------------------------------------------------------------------------------
# # Example cache structure:
# # ---------------------------------------------------------------------------------------------------------------
# # cache = {
# #     ("PSX.APL", "1m"): {
# #         "bars": [  # Recent OHLCV data
# #             {"timestamp": ..., "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...},
# #             ...
# #         ],
# #         "indicators": {
# #             "sma": [...],        # list of computed SMA values
# #             "ema": [...],
# #             "rsi": [...],
# #             "macd": [...],
# #             "macd_signal": [...],
# #             "macd_hist": [...],
# #             "supertrend": [...]
# #         }
# #     },
# #     ...
# # }
# # ---------------------------------------------------------------------------------------------------------------

# def initialize_symbol(symbol: str, timeframe: str) -> None:
#     """Ensure symbol-timeframe entry exists in the cache."""
#     _ = _cache[(symbol, timeframe)]  # Triggers defaultdict creation


# def append_bar(symbol: str, timeframe: str, bar: dict) -> None:
#     """Append a new OHLCV bar to the cache."""
#     initialize_symbol(symbol, timeframe)
#     _cache[(symbol, timeframe)]["bars"].append(bar)


# def get_bars(symbol: str, timeframe: str) -> list:
#     """Retrieve the list of bars for a symbol-timeframe."""
#     return list(_cache[(symbol, timeframe)]["bars"])


# def set_indicator(symbol: str, timeframe: str, name: str, values: list) -> None:
#     """Set the computed values of an indicator for a symbol-timeframe."""
#     initialize_symbol(symbol, timeframe)
#     _cache[(symbol, timeframe)]["indicators"][name.lower()] = values


# def get_indicator(symbol: str, timeframe: str, name: str) -> list:
#     """Get the computed values of an indicator, or an empty list if not present."""
#     return _cache[(symbol, timeframe)]["indicators"].get(name.lower(), [])


# def clear_cache() -> None:
#     """Clear the entire in-memory cache (for debugging or resetting)."""
#     _cache.clear()
