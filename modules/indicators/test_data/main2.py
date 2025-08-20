
import pandas as pd
import numpy as np

from indicators.calculator import sma, ema, rsi, macd, supertrend

def main():
    """
    Main function to read market data from the new CSV format
    and calculate technical indicators using TradingView-style methods.
    """
    try:
        # Load the stock market data from the CSV file
        # Ensure your new CSV file is named 'kse100.csv' or change the filename below.
        df = pd.read_csv('BOP.csv')

        # --- Data Cleaning and Preparation ---

        # The data is in reverse chronological order (newest first), so we must reverse it.
        df = df.iloc[::-1].reset_index(drop=True)

        # Define the columns we need from the new format
        required_columns = ['open', 'high', 'low', 'close']
        
        # Check if all required columns exist
        if not all(col in df.columns for col in required_columns):
            print(f"Error: CSV must contain the columns: {required_columns}")
            print(f"Found columns: {list(df.columns)}")
            return
            
        # The new format doesn't have commas, so we can directly use the columns.
        # Ensure data is float, in case it was read as string.
        for col in required_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows with missing values that might have been created by 'coerce'
        df.dropna(subset=required_columns, inplace=True)

        # Get the data into lists for the indicator functions
        closes = df['close'].tolist()
        highs = df['high'].tolist()
        lows = df['low'].tolist()

        print("--- BOP Technical Indicator Analysis (TradingView Style) ---")
        print(f"Using {len(closes)} data points for calculation.\n")

        # --- Calculate and Display Indicators ---

        # 1. Simple Moving Average (SMA) - 20 Day
        period_sma = 20
        sma_values = sma(closes, period_sma)
        if sma_values and sma_values[-1] is not None and not np.isnan(sma_values[-1]):
            print(f"Simple Moving Average (SMA-{period_sma}): {sma_values[-1]:.2f}")
        else:
            print(f"SMA-{period_sma}: Not enough data.")

        # 2. Exponential Moving Average (EMA) - 20 Day
        period_ema = 20
        ema_values = ema(closes, period_ema)
        if ema_values and ema_values[-1] is not None and not np.isnan(ema_values[-1]):
            print(f"Exponential Moving Average (EMA-{period_ema}): {ema_values[-1]:.2f}")
        else:
            print(f"EMA-{period_ema}: Not enough data.")

        # 3. Relative Strength Index (RSI) - 14 Day
        period_rsi = 14
        rsi_values = rsi(closes, period_rsi)
        if rsi_values and rsi_values[-1] is not None and not np.isnan(rsi_values[-1]):
            print(f"Relative Strength Index (RSI-{period_rsi}): {rsi_values[-1]:.2f}")
        else:
            print(f"RSI-{period_rsi}: Not enough data.")

        # 4. Moving Average Convergence Divergence (MACD)
        macd_lines, signal_lines, _ = macd(closes)
        if macd_lines and macd_lines[-1] is not None and not np.isnan(macd_lines[-1]):
            print(f"MACD (12, 26, 9):")
            print(f"  - MACD Line:   {macd_lines[-1]:.2f}")
            print(f"  - Signal Line: {signal_lines[-1]:.2f}")
        else:
            print("MACD: Not enough data.")

        # 5. SuperTrend
        st_lines, st_directions = supertrend(highs, lows, closes)
        if st_lines and st_lines[-1] is not None and st_lines[-1] > 0:
            direction = "UP" if st_directions[-1] == 1 else "DOWN"
            print(f"SuperTrend (7, 3):")
            print(f"  - Trend Direction: {direction}")
            print(f"  - Trend Line:      {st_lines[-1]:.2f}")
        else:
            print("SuperTrend: Not enough data.")

    except FileNotFoundError:
        print("Error: 'kse100.csv' not found.")
        print("Please make sure the CSV file is in the same directory as this script.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
