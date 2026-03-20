# 🛡️ FX Intelligence: Technical Explanation

This document provides a comprehensive, layer-by-layer breakdown of how the FX Intelligence Platform operates, from raw data ingestion to technical visualization.

---

## 🏗️ Architecture Overview

The system follows a classic **Three-Tier Architecture** tailored for time-series financial data:

1.  **Ingestion Layer (The Engine):** High-frequency fetching and standardization.
2.  **Persistence Layer (The Vault):** Scalable time-series storage.
3.  **Visualization Layer (The Desk):** Analytical processing and UI rendering.

---

## 1. The Ingestion Layer (`backend/`)

This layer is responsible for maintaining the "Source of Truth" in our database.

### `fx_fetcher.py`
This module acts as a specialized wrapper for the `yfinance` library. It performs several critical tasks:
-   **Multi-Pair Fetching:** Requests data for multiple tickers (USDINR=X, EURUSD=X, etc.) in a single batch.
-   **Timestamp Standardization:** Converts all incoming data into a consistent UTC timezone format.
-   **Data Cleaning:** Filters out empty records or "NaN" anomalies that often occur during market holidays.

### `fx_scheduler.py`
This is the "brain" of the backend. It coordinates the flow of data:
-   **Stateful Sync:** It fetches historical windows (defaulting to 5 years) to ensure the UI has plenty of depth.
-   **Upsert Logic:** Instead of just "inserting", it uses a **Postgres Upsert** (ON CONFLICT). This ensures that if we fetch the same data twice, it replaces the existing record rather than creating a duplicate.

---

## 2. The Persistence Layer (Supabase)

We use **Supabase** (PostgreSQL) because it handles time-series data efficiently and provides a high-performance REST API (Postgrest) for our dashboard to consume.

-   **Table: `fx_rates`**
    -   `timestamp` (Primary Key Part 1): Precise UTC time of the record.
    -   `pair` (Primary Key Part 2): The ticker symbol.
    -   `close`: The final closing price for that period.

---

## 3. The Visualization Layer (`dashboard/fx_app.py`)

This is where raw numbers are transformed into **Market Intelligence**.

### Technical Analysis (The "Numbers")
The dashboard calculates several specialized metrics on-the-fly:

-   **Returns Calculation:** We compare the most recent price against historical points (1 Day, 7 Days, etc.) to calculate percentage change.
    -   `Formula: ((Current - Historical) / Historical) * 100`

-   **Rolling Volatility:** We calculate the standard deviation of percentage changes over a 30-day window, then multiply by $\sqrt{252}$ to "Annualize" it. This tells an investor: *"Based on the last month, how much could this currency swing in a year?"*

-   **Drawdown (Peak-to-Trough):** One of the most important risk metrics.
    -   We identify the highest price (Peak) in the current window.
    -   We calculate how far the current price has dropped from that peak.
    -   It helps investors understand the "worst-case scenario" they would have faced if they bought at the top.

---

## 4. UI/UX Design Philosophy

The dashboard is built with a **"High-Contrast, Low-Noise"** philosophy:
-   **Contextual Hovering:** Descriptions for currency pairs are hidden behind tooltips to keep the main view clean.
-   **Visual Hierarchy:** High-priority "Snapshots" are at the top, followed by interactive charts, with deeper "Audit" logs at the bottom.
-   **Status Indication:** Color coding (Green for gains, Red for losses) is used sparingly but effectively to provide instant sentiment.

---

## 🏁 Summary for Collaborators

If you are joining this project, focus on `backend/fx_scheduler.py` if you want to change how data is saved, or `dashboard/fx_app.py` if you want to add new charts or technical indicators.
