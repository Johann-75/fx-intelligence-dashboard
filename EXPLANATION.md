# FOREX Intelligence Dashboard: Architecture & Data Flow

This document provides a highly detailed explanation of the **FOREX Intelligence Dashboard** application, breaking down its architecture, backend data ingestion pipelines, frontend components, and how everything connects.

## Overview

The **FOREX Intelligence Dashboard** is a full-stack, end-to-end data analytics web application built with Python. Its primary purpose is to provide real-time and historical analytics for major foreign exchange (FX) currency pairs. 

At a high level, the application consists of two main parts:
1. **The Backend (Data Ingestion)**: Python scripts that fetch financial data from Yahoo Finance and store it securely into a Supabase PostgreSQL database.
2. **The Frontend (Streamlit Dashboard)**: A web-based user interface built with Streamlit that retrieves data from the Supabase database, computes financial metrics (returns, volatility, drawdowns), and displays interactive charts using Plotly.

---

## 1. Project Structure

```text
currency_dashboard/
├── .env                  # Environment variables (Supabase URL & API Keys)
├── README.md             # Standard project readme
├── backend/
│   ├── fx_fetcher.py     # Module for pulling data from Yahoo Finance
│   └── fx_scheduler.py   # Main data ingestion script that upserts data to Supabase
└── dashboard/
    └── fx_app.py         # The Streamlit frontend application
```

---

## 2. The Backend: Data Ingestion & Storage

The backend is responsible for sourcing the data and pushing it to a centralized database. Reliable data is the backbone of any intelligence dashboard. Let's break down the backend scripts.

### 2.1. `fx_fetcher.py` (The Data Sourcing Layer)

This script contains the logic to connect to the external data provider, Yahoo Finance, using the `yfinance` Python library.

- **Functionality**: The core function `fetch_fx_data(pairs, period)` takes a list of currency ticker symbols (e.g., `USDINR=X`, `EURUSD=X`) and a time period (e.g., `"5y"` for 5 years).
- **Process**:
  1. It iterates over each ticker and calls `yf.Ticker(pair).history()` to download the Daily historical data.
  2. The DataFrame is cleaned up to retain only the `Date` and `Close` columns (which are renamed to `timestamp` and `close`).
  3. The `pair` symbol is added as a column to identify the currency.
  4. Crucially, the timestamp timezone is standardized to `UTC` to prevent any timezone mismatch issues when saving to the database.
  5. Finally, all the individual currency DataFrames are concatenated into one massive DataFrame and returned.

### 2.2. `fx_scheduler.py` (The Pipeline Layer)

This script acts as the orchestrator. It uses `fx_fetcher.py` to get the data, and then securely transmits it to Supabase. This script can be run manually or set up on a cron job (scheduler) to update the database daily.

- **Supabase Integration**: It uses the `.env` file to load `SUPABASE_URL` and `SUPABASE_KEY`. Instead of using an ORM or the Supabase Python client, this script makes direct REST API `POST` requests to the PostgREST endpoint of the Supabase database.
- **The Upsert Mechanism**: 
  - The function `upsert_fx_data(...)` takes the DataFrame, converts the timestamps to ISO format strings (`%Y-%m-%dT%H:%M:%S%z`), and sends it as a JSON payload.
  - The API requests use the header `"Prefer": "resolution=merge-duplicates"`. This is an **"upsert"** operation—it updates existing rows if the timestamp already exists, and inserts new rows if they are fresh. This prevents duplicate data entries in the database.
- **Batching**: To improve network reliability and avoid API limits, the data is pushed in chunks of 1000 rows.
- **Execution**: The main block defines a hardcoded list of the 5 tracked pairs (USD/INR, EUR/USD, GBP/USD, USD/JPY, and the DXY Dollar Index) and executes the ingestion pipeline.

---

## 3. The Frontend: `fx_app.py`

This is the user-facing Streamlit application. Streamlit runs as an active Python server, dynamically rendering the UI components when a user visits the webpage.

### 3.1. Initialization & Styling
- The application sets up a custom UI configuration via `st.set_page_config()` to establish a wide layout and a dark aesthetic.
- A significant block of raw CSS is injected via `st.markdown(..., unsafe_allow_html=True)`. This custom styles the sidebar, creates premium "glassmorphic" gradient boxes for metrics (`.snapshot-card`), formats volatility cards, and colors positive/negative returns.
- **Mapping Layer**: A dictionary `TICKER_MAP` is used to translate ugly Yahoo Finance tickers (`USDINR=X`) into user-friendly names (`USD/INR`).

### 3.2. Data Loading (`load_all_data`)
- Unlike standard apps that might query `yfinance` exactly when the user opens the app (which is slow and rate-limited), this dashboard queries the Supabase database directly via REST GET requests.
- **Pagination**: Supabase restricts responses to 1,000 rows by default. The script effectively handles pagination using a `while True` loop and `Offset` headers to pull down all historical data.
- **Caching**: The function uses `@st.cache_data(ttl=600)`, which holds the downloaded database in the server's RAM for 10 minutes. When subsequent users open the app, it loads instantly without needing to ping Supabase again.

### 3.3. Analytics Helpers
The dashboard contains custom Python functions to process financial mathematics on the fly:
- `compute_returns()`: Calculates percentage change from the last closing price to various historical offsets (1-day, 7-day, 30-day, etc.).
- `rolling_vol_series()`: Computes Annualized Volatility. It measures the standard deviation of daily percentage changes over a 30-day rolling window, multiplied by the square root of 252 (trading days in a year).
- `compute_drawdown_stats()`: A risk management metric. It traces the highest historical point of a currency (the "peak") and measures how far the current price has fallen below that peak in percentage terms (the "trough").

### 3.4. Page Layout & Interactions
The UI is divided into several interactive blocks:

- **Sidebar Configuration**: The user can multi-select currency pairs, adjust the historical window (30 Days to 3 Years), toggle basic normalization (setting starting points to 100 for easy comparison), and toggle Moving Averages.
- **Block 1: Market Snapshot**: Visualizes the current closing price and recent percentage changes dynamically. Green for positive returns, red for negative.
- **Block 2: Trend Analysis**: Generates interactive time-series line charts using `plotly`. If enabled, it overlays 20-Day and 50-Day Simple Moving Averages to show momentum.
- **Block 3: Volatility Metrics**: Displays the 30-day Annualized Volatility compared to the 2-Year historical average. This tells the user if the currency is acting chaotic or calm relative to its norm.
- **Block 4: Drawdown Analysis**: Renders an area chart showing the depth of price drops over time, helping analyze currency resilience.
- **Block 5: Data Engineering Audit**: A footer section transparently displaying how many database rows fuel the current view, acting as a data integrity check.

## Summary 

1. **`backend/fx_scheduler.py`** gets executed. It calls **`fx_fetcher.py`** to get Yahoo Finance data.
2. The data is transformed and securely upserted straight into **Supabase PostgreSQL**.
3. A user opens the browser to view local port `8501`.
4. **`dashboard/fx_app.py`** executes, instantly fetching data from **Supabase** (or from RAM cache).
5. The frontend computes the dynamic math (Returns, Volatility, Moving Averages) and renders the dark, interactive Plotly dashboard.
