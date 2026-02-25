import os
import pandas as pd
import requests
from dotenv import load_dotenv
import sys
import json

# Add parent directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from fx_fetcher import fetch_fx_data

load_dotenv()

tickers = [
    "USDINR=X",
    "EURUSD=X",
    "GBPUSD=X",
    "USDJPY=X",
    "DX-Y.NYB"
]

try:
    print("Fetching data for 2 days...")
    df = fetch_fx_data(tickers, period="2d")
    print(f"Fetched {len(df)} rows.")
    print("Columns:", df.columns.tolist())
    print("Types:\n", df.dtypes)
    print("\nSample records:")
    # Print as JSON format that would be sent to Supabase
    records = df.copy()
    records['timestamp'] = records['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    data_to_upsert = records.to_dict(orient='records')
    print(json.dumps(data_to_upsert[:5], indent=2))
    
    # Check for NaNs
    print("\nNaN counts:")
    print(df.isna().sum())
    
except Exception as e:
    print(f"Error: {e}")
