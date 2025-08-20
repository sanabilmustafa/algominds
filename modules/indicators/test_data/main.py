import pandas as pd

def sma(prices, period):
    """Calculates the Simple Moving Average (SMA) for a series."""
    if len(prices) < period:
        return [None] * len(prices)
    return pd.Series(prices).rolling(window=period).mean().tolist()

def ema(prices, period):
    """
    Calculates the Exponential Moving Average (EMA) for a series.
    This uses a standard formula that aligns with charting platforms.
    """
    if len(prices) < period:
        return [None] * len(prices)
    return pd.Series(prices).ewm(span=period, adjust=False).mean().tolist()

def rsi(prices, period=14):
    """
    Calculates the Relative Strength Index (RSI) using Wilder's Smoothing.
    This is the standard method used on platforms like TradingView.
    """
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

def macd(prices, fast=12, slow=26, signal=9):
    """
    Calculates the Moving Average Convergence Divergence (MACD).
    Returns three lists: MACD line, Signal line, and Histogram.
    """
    if len(prices) < slow:
        return [None] * len(prices), [None] * len(prices), [None] * len(prices)

    prices_series = pd.Series(prices)
    fast_ema = prices_series.ewm(span=fast, adjust=False).mean()
    slow_ema = prices_series.ewm(span=slow, adjust=False).mean()
    
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line.tolist(), signal_line.tolist(), histogram.tolist()

def supertrend(highs, lows, closes, period=7, multiplier=3):
    """
    Calculates the SuperTrend indicator.
    This is a stateful calculation that tracks the trend direction.
    Returns two lists: the SuperTrend line and the direction (-1 for down, 1 for up).
    """
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






# def main():
#     """
#     Main function to read market data and calculate technical indicators.
#     """
#     try:
#         # Load the stock market data from the CSV file
#         # Make sure 'kse100.csv' is in the same directory as this script.
#         df = pd.read_csv('kse100.csv')
        
#         # Ensure the column names are what we expect.
#         # Common names are 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'
#         # We will assume the 'Close' column for most price-based calculations.
#         # Please adjust the column names below if your CSV has different headers.
#         required_columns = ['High', 'Low', 'Close']
#         if not all(col in df.columns for col in required_columns):
#             print(f"Error: CSV must contain the columns: {required_columns}")
#             print(f"Found columns: {list(df.columns)}")
#             return

#         # Convert price columns to lists for the indicator functions
#         closes = df['Close'].tolist()
#         highs = df['High'].tolist()
#         lows = df['Low'].tolist()

#         print("--- KSE-100 Technical Indicator Analysis ---")
#         print(f"Data based on the latest {len(closes)} trading days.\n")

#         # --- Calculate and Display Indicators ---

#         # 1. Simple Moving Average (SMA) - 20 Day
#         period_sma = 20
#         sma_value = sma(closes, period_sma)
#         if sma_value is not None:
#             print(f"Simple Moving Average (SMA-{period_sma}): {sma_value:.2f}")
#         else:
#             print(f"SMA-{period_sma}: Not enough data.")

#         # 2. Exponential Moving Average (EMA) - 20 Day
#         period_ema = 20
#         ema_value = ema(closes, period_ema) # Simplified call, see function for stateful EMA
#         if ema_value is not None:
#             print(f"Exponential Moving Average (EMA-{period_ema}): {ema_value:.2f}")
#         else:
#             print(f"EMA-{period_ema}: Not enough data.")

#         # 3. Relative Strength Index (RSI) - 14 Day
#         period_rsi = 14
#         rsi_value = rsi(closes, period_rsi)
#         if rsi_value is not None:
#             print(f"Relative Strength Index (RSI-{period_rsi}): {rsi_value:.2f}")
#         else:
#             print(f"RSI-{period_rsi}: Not enough data.")

#         # 4. Moving Average Convergence Divergence (MACD)
#         macd_line, signal_line = macd(closes)
#         if macd_line is not None and signal_line is not None:
#             print(f"MACD (12, 26, 9):")
#             print(f"  - MACD Line:   {macd_line:.2f}")
#             print(f"  - Signal Line: {signal_line:.2f}")
#         else:
#             print("MACD: Not enough data.")

#         # 5. SuperTrend
#         st_result = supertrend(highs, lows, closes)
#         if st_result is not None:
#             print(f"SuperTrend (7, 3):")
#             print(f"  - Trend Direction: {st_result['direction'].upper()}")
#             print(f"  - Trend Line:      {st_result['supertrend']:.2f}")
#         else:
#             print("SuperTrend: Not enough data.")

#     except FileNotFoundError:
#         print("Error: 'kse100.csv' not found.")
#         print("Please make sure the CSV file is in the same directory as this script.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")


def main():
    """
    Main function to read market data and calculate technical indicators.
    """
    try:
        # Load the stock market data from the CSV file
        # Make sure 'kse100.csv' is in the same directory as this script.
        df = pd.read_csv('kse100.csv')

        # --- Data Cleaning and Preparation ---

        # The data is in reverse chronological order, so we need to reverse it.
        df = df.iloc[::-1].reset_index(drop=True)

        # Define the columns we need to process
        # The 'Price' column will be used as the 'Close' price.
        price_columns = ['Price', 'Open', 'High', 'Low']
        
        # Check if all required columns exist
        if not all(col in df.columns for col in price_columns):
            print(f"Error: CSV must contain the columns: {price_columns}")
            print(f"Found columns: {list(df.columns)}")
            return
            
        # Clean the numeric columns by removing commas and converting to float
        for col in price_columns:
            df[col] = df[col].str.replace(',', '', regex=False).astype(float)

        # Convert price columns to lists for the indicator functions
        closes = df['Price'].tolist()
        highs = df['High'].tolist()
        lows = df['Low'].tolist()

        print("--- KSE-100 Technical Indicator Analysis ---")
        print(f"Data based on the latest {len(closes)} trading days.\n")

        # --- Calculate and Display Indicators ---

        # 1. Simple Moving Average (SMA) - 20 Day
        period_sma = 20
        sma_value = sma(closes, period_sma)
        if sma_value is not None:
            print(f"Simple Moving Average (SMA-{period_sma}): {sma_value:.2f}")
        else:
            print(f"SMA-{period_sma}: Not enough data.")

        # 2. Exponential Moving Average (EMA) - 20 Day
        period_ema = 20
        ema_value = ema(closes, period_ema)
        if ema_value is not None:
            print(f"Exponential Moving Average (EMA-{period_ema}): {ema_value:.2f}")
        else:
            print(f"EMA-{period_ema}: Not enough data.")

        # 3. Relative Strength Index (RSI) - 14 Day
        period_rsi = 14
        rsi_value = rsi(closes, period_rsi)
        if rsi_value is not None:
            print(f"Relative Strength Index (RSI-{period_rsi}): {rsi_value:.2f}")
        else:
            print(f"RSI-{period_rsi}: Not enough data.")

        # 4. Moving Average Convergence Divergence (MACD)
        macd_line, signal_line = macd(closes)
        if macd_line is not None and signal_line is not None:
            print(f"MACD (12, 26, 9):")
            print(f"  - MACD Line:   {macd_line:.2f}")
            print(f"  - Signal Line: {signal_line:.2f}")
        else:
            print("MACD: Not enough data.")

        # 5. SuperTrend
        st_result = supertrend(highs, lows, closes)
        if st_result is not None:
            print(f"SuperTrend (7, 3):")
            print(f"  - Trend Direction: {st_result['direction'].upper()}")
            print(f"  - Trend Line:      {st_result['supertrend']:.2f}")
        else:
            print("SuperTrend: Not enough data.")

    except FileNotFoundError:
        print("Error: 'kse100.csv' not found.")
        print("Please make sure the CSV file is in the same directory as this script.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()