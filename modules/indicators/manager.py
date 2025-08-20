#  Indicator Engine (Smart Update Loop)
# ---------------------------------------------------------------------------------------------------------------
# MANAGER structure:
# ---------------------------------------------------------------------------------------------------------------

# ✅ Goals Recap for manager.py
# This module will:

# Track subscriptions for (symbol, timeframe, indicator_name)
# Process new incoming bars:
    # Store them in cache.
    # Trigger relevant indicator calculations.
    # Update the cache with the computed values.
# Expose a public API:
    # Subscribe to indicators.
    # Unsubscribe.
    # Receive new bars and route to calculator/state.
    
    
# LAYOUT PLAN:
# manager.py

# from .state import add_bar, get_bars, update_indicator, get_indicator, is_subscribed
# from .calculator import calculate_rsi, calculate_sma, ...
# from collections import defaultdict

# # Track subscriptions like: subscriptions[("PSO", "15m")] = {"RSI", "SMA", "MACD"}
# subscriptions = defaultdict(set)

# # === Subscription Management ===

# def subscribe(symbol, timeframe, indicator_name):
#     """Subscribe to a new indicator for a given symbol+timeframe."""
#     subscriptions[(symbol, timeframe)].add(indicator_name)

# def unsubscribe(symbol, timeframe, indicator_name):
#     """Unsubscribe from an indicator."""
#     subscriptions[(symbol, timeframe)].discard(indicator_name)

# def list_subscriptions(symbol, timeframe):
#     """List all subscribed indicators for a symbol+timeframe."""
#     return subscriptions.get((symbol, timeframe), set())

# # === Core Processing Logic ===

# def on_new_bar(symbol, timeframe, bar_data):
#     """
#     Entry point when new bar data is received.
#     1. Store bar in cache.
#     2. Check subscriptions.
#     3. Compute & store indicator values.
#     """
#     add_bar(symbol, timeframe, bar_data)
#     bars = get_bars(symbol, timeframe)

#     for indicator in list_subscriptions(symbol, timeframe):
#         value = _calculate_indicator(indicator, bars)
#         if value is not None:
#             update_indicator(symbol, timeframe, indicator, value)

# # === Internal Dispatcher ===

# def _calculate_indicator(indicator, bars):
#     """Dispatch to the correct calculator function based on the indicator name."""
#     try:
#         if indicator == "RSI":
#             return calculate_rsi(bars)
#         elif indicator == "SMA":
#             return calculate_sma(bars)
#         elif indicator == "EMA":
#             return calculate_ema(bars)
#         elif indicator == "MACD":
#             return calculate_macd(bars)
#         elif indicator == "SuperTrend":
#             return calculate_supertrend(bars)
#         else:
#             raise ValueError(f"Unknown indicator: {indicator}")
#     except Exception as e:
#         print(f"[Indicator Error] {indicator} failed: {e}")
#         return None

# # === Optional: Access Latest Indicator Value ===

# def get_latest_indicator_value(symbol, timeframe, indicator):
#     """Get the most recent computed value for an indicator."""
#     return get_indicator(symbol, timeframe, indicator)


# 🔁 Typical Flow
# Some external service calls:
    # subscribe("PSO", "15m", "RSI")

# Then when new bar data comes in:
    # on_new_bar("PSO", "15m", new_bar_dict)    

# The system:
    # Saves the bar.
    # Checks subscriptions.
    # Computes RSI from calculator.
    # Updates cache in state.py.


# 🔧 Future-Proofing Notes
# We could later expand:
    # Dynamic indicator parameters (e.g. RSI(14), SMA(50))
    # Persistence (optional)
    # Per-user subscription management
    # Task queues / batch jobs if data volume increases
# ---------------------------------------------------------------------------------------------------------------

from collections import defaultdict
from .state import append_bar, get_bars, set_indicator, get_indicator
from .calculator import (
    rsi, sma, ema, macd, supertrend
)

subscriptions = defaultdict(set)

def subscribe(symbol, timeframe, indicator_name):
    subscriptions[(symbol, timeframe)].add(indicator_name)

def unsubscribe(symbol, timeframe, indicator_name):
    subscriptions[(symbol, timeframe)].discard(indicator_name)

def list_subscriptions(symbol, timeframe):
    return subscriptions.get((symbol, timeframe), set())

def _calculate_indicator(indicator, bars):
    try:
        if indicator == "RSI":
            return rsi(bars)
        elif indicator == "SMA":
            return sma(bars)
        elif indicator == "EMA":
            return ema(bars)
        elif indicator == "MACD":
            return macd(bars)
        elif indicator == "SuperTrend":
            return supertrend(bars)
        else:
            raise ValueError(f"Unknown indicator: {indicator}")
    except Exception as e:
        print(f"[Indicator Error] {indicator} failed: {e}")
        return None

def on_new_bar(symbol, timeframe, bar_data=None):
    if bar_data:
        append_bar(symbol, timeframe, bar_data)

    bars = get_bars(symbol, timeframe)
    if not bars:
        return

    for indicator in list_subscriptions(symbol, timeframe):
        result = _calculate_indicator(indicator, bars)
        if result is not None:
            set_indicator(symbol, timeframe, indicator, result)
            
def get_latest_indicator_value(symbol, timeframe, indicator):
    return get_indicator(symbol, timeframe, indicator)

async def calculate_indicator_for_symbol(symbol: str, indicator: str):
    """
    Fetches bars for the symbol and calculates the specified indicator.
    This is the main function to call from indicator_handler.py
    """
    bars = get_bars(symbol)

    if not bars or len(bars) < 10:  # Optional: minimum length check
        print(f"[Indicator] Not enough bars to calculate {indicator} for {symbol}")
        return None

    return _calculate_indicator(indicator, bars)