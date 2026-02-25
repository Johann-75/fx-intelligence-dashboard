import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_fx_data(pairs: list[str], period: str = "5y") -> pd.DataFrame:
    """
    Fetches historical FX data for given pairs using yfinance.
    
    Args:
        pairs: List of FX tickers (e.g., ['USDINR=X', 'EURUSD=X'])
        period: Period to fetch (default "5y")
        
    Returns:
        DataFrame with columns [timestamp, pair, close]
    """
    all_data = []
    
    for pair in pairs:
        print(f"Fetching data for {pair}...")
        ticker = yf.Ticker(pair)
        df = ticker.history(period=period, interval="1d")
        
        if df.empty:
            print(f"Warning: No data found for {pair}")
            continue
            
        # Clean and format data
        df = df.reset_index()
        df = df[['Date', 'Close']]
        df.columns = ['timestamp', 'close']
        df['pair'] = pair
        
        # Ensure timestamp is TZ-aware (yfinance usually returns UTC-aware or TZ-naive depending on source)
        if df['timestamp'].dt.tz is None:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
        else:
            df['timestamp'] = df['timestamp'].dt.tz_convert('UTC')
            
        all_data.append(df)
    
    if not all_data:
        raise ValueError("Failed to fetch data for any of the requested pairs.")
        
    result_df = pd.concat(all_data, ignore_index=True)
    return result_df[['timestamp', 'pair', 'close']]

if __name__ == "__main__":
    # Test fetch
    try:
        data = fetch_fx_data(['USDINR=X', 'EURUSD=X'], period="1mo")
        print(data.head())
        print(f"Total rows: {len(data)}")
    except Exception as e:
        print(f"Error: {e}")


