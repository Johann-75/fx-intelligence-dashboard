import sys
import os
import json
import pandas as pd
import requests

# Ensure we can import from the same directory when run from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fx_fetcher import fetch_fx_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    sys.exit(1)

def upsert_fx_data(df: pd.DataFrame):
    """
    Upserts FX data into Supabase fx_rates table using direct REST API.
    """
    if df.empty:
        print("No data to upsert.")
        return

    # Prepare records for Supabase
    records = df.copy()
    # Use .map() directly on the Series
    records['timestamp'] = records['timestamp'].map(lambda x: x.isoformat())
    data_to_upsert = records.to_dict(orient='records')

    # Postgrest endpoint
    url = f"{SUPABASE_URL}/rest/v1/fx_rates?on_conflict=pair,timestamp"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data_to_upsert))
        if response.status_code != 201 and response.status_code != 200:
             print(f"Supabase Error {response.status_code}: {response.text}")
             print(f"Sample data sent: {data_to_upsert[0] if data_to_upsert else 'Empty'}")
        response.raise_for_status()
        print(f"Successfully upserted {len(data_to_upsert)} rows.")
        return response
    except Exception as e:
        if hasattr(e, 'response') and e.response is not None:
             print(f"Supabase Response Text: {e.response.text}")
        print(f"Error during upsert: {e}")
        raise

def run_ingestion(pairs: list[str], period: str = "5y"):
    """
    Main ingestion flow: fetch -> upsert.
    """
    print(f"Starting ingestion for {pairs} over {period}...")
    try:
        df = fetch_fx_data(pairs, period=period)
        
        # Drop rows with NaN values which can cause 400 errors in Supabase
        df = df.dropna()
        
        # Drop duplicates in case yfinance returns some (rare but possible)
        df = df.drop_duplicates(subset=['timestamp', 'pair'])

        # Batch upsert if data is large
        chunk_size = 10
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            try:
                upsert_fx_data(chunk)
            except Exception as e:
                # If chunk failed, try row-by-row as fallback
                all_conflicts = True
                for ridx, row in chunk.iterrows():
                    try:
                        upsert_fx_data(pd.DataFrame([row]))
                    except Exception as inner_e:
                        if "409" in str(inner_e):
                            continue
                        all_conflicts = False
                        print(f"BAD ROW: {row.to_dict()}")
                        print(f"REASON: {inner_e}")
                
                # Only raise if there were real errors (not just conflicts)
                if not all_conflicts:
                    raise e
            
        print("Ingestion completed successfully.")
    except Exception as e:
        print(f"FATAL: Ingestion failed. {e}")
        sys.exit(1)

if __name__ == "__main__":
    tickers = [
        "USDINR=X"
    ]
    
    import argparse
    parser = argparse.ArgumentParser(description="FX Data Ingestor")
    parser.add_argument("--period", type=str, default="5y", help="Period to fetch (e.g., 5y, 1mo, 1d)")
    args = parser.parse_args()
    
    run_ingestion(tickers, period=args.period)
