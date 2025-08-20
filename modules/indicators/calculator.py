import pandas as pd

# Define the filename
filename = "output.txt"

# Write content to the file

def sma(bars, period=9):
    """Calculates the Simple Moving Average (SMA) for a series."""
    prices = [bar["close"] for bar in bars]
    if len(prices) < period:
        return [None] * len(prices)
    sma_values = pd.Series(prices).rolling(window=period).mean().tolist()
    return [round(val, 2) if val is not None else None for val in sma_values]

def ema(bars, period=9):
    """
    Calculates the Exponential Moving Average (EMA) for a series.
    This uses a standard formula that aligns with charting platforms.
    """
    prices = [bar["close"] for bar in bars]
    if len(prices) < period:
        return [None] * len(prices)
    ema_value = pd.Series(prices).ewm(span=period, adjust=False).mean().tolist()
    return [round(val, 2) if val is not None else None for val in ema_value]

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
    with open(filename, "w") as file:
        file.write(str(prices))
        file.write(str(rsi))
        file.close()
    return [round(val, 2) if val is not None else None for val in rsi.tolist()]

def macd(bars, fast=12, slow=26, signal=9):
    """
    Calculates the Moving Average Convergence Divergence (MACD).
    Returns three lists: MACD line, Signal line, and Histogram.
    """
    prices = [bar["close"] for bar in bars]
    if len(prices) < slow:
        return [None] * len(prices), [None] * len(prices), [None] * len(prices)

    prices_series = pd.Series(prices)
    fast_ema = prices_series.ewm(span=fast, adjust=False).mean()
    slow_ema = prices_series.ewm(span=slow, adjust=False).mean()
    
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line.tolist(), signal_line.tolist(), histogram.tolist()

def supertrend(bars, period=7, multiplier=3):
    """
    Calculates the SuperTrend indicator.
    This is a stateful calculation that tracks the trend direction.
    Returns two lists: the SuperTrend line and the direction (-1 for down, 1 for up).
    """
    highs = [bar["high"] for bar in bars]
    lows = [bar["low"] for bar in bars]
    closes = [bar["close"] for bar in bars]
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("Input lists must be the same length.")

    if len(closes) < period:
        return [None] * len(closes), [None] * len(closes)

    df = pd.DataFrame({
        'High': highs,
        'Low': lows,
        'Close': closes
    })

    # Calculate ATR (Average True Range)
    df['tr0'] = abs(df['High'] - df['Low'])
    df['tr1'] = abs(df['High'] - df['Close'].shift())
    df['tr2'] = abs(df['Low'] - df['Close'].shift())
    df['TR'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
    df['ATR'] = df['TR'].ewm(alpha=1/period, adjust=False).mean()

    # Calculate Basic Upper and Lower Bands
    df['basic_upperband'] = (df['High'] + df['Low']) / 2 + multiplier * df['ATR']
    df['basic_lowerband'] = (df['High'] + df['Low']) / 2 - multiplier * df['ATR']

    # Calculate Final Upper and Lower Bands
    df['final_upperband'] = 0.0
    df['final_lowerband'] = 0.0
    for i in range(period, len(df)):
        if df.loc[i-1, 'Close'] <= df.loc[i-1, 'final_upperband']:
            df.loc[i, 'final_upperband'] = min(df.loc[i, 'basic_upperband'], df.loc[i-1, 'final_upperband'])
        else:
            df.loc[i, 'final_upperband'] = df.loc[i, 'basic_upperband']

        if df.loc[i-1, 'Close'] >= df.loc[i-1, 'final_lowerband']:
            df.loc[i, 'final_lowerband'] = max(df.loc[i, 'basic_lowerband'], df.loc[i-1, 'final_lowerband'])
        else:
            df.loc[i, 'final_lowerband'] = df.loc[i, 'basic_lowerband']

    # Calculate SuperTrend
    df['supertrend'] = 0.0
    df['direction'] = 0
    for i in range(period, len(df)):
        if df.loc[i-1, 'supertrend'] == df.loc[i-1, 'final_upperband']:
            if df.loc[i, 'Close'] <= df.loc[i, 'final_upperband']:
                df.loc[i, 'supertrend'] = df.loc[i, 'final_upperband']
                df.loc[i, 'direction'] = -1
            else:
                df.loc[i, 'supertrend'] = df.loc[i, 'final_lowerband']
                df.loc[i, 'direction'] = 1
        elif df.loc[i-1, 'supertrend'] == df.loc[i-1, 'final_lowerband']:
            if df.loc[i, 'Close'] >= df.loc[i, 'final_lowerband']:
                df.loc[i, 'supertrend'] = df.loc[i, 'final_lowerband']
                df.loc[i, 'direction'] = 1
            else:
                df.loc[i, 'supertrend'] = df.loc[i, 'final_upperband']
                df.loc[i, 'direction'] = -1

    return df['supertrend'].tolist(), df['direction'].tolist()

