import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

url = f"{SUPABASE_URL}/rest/v1/fx_rates?select=timestamp,pair,close&order=timestamp.desc&limit=10"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Latest 10 records in Supabase:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error: {e}")
