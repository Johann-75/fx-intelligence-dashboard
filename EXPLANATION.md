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
-   **USD/INR Specialization:** Focused fetching and standardization for the Indian Rupee exchange rate.
-   **Timestamp Standardization:** Converts all incoming data into a consistent UTC timezone format.
-   **Data Cleaning:** Filters out empty records or 'NaN' anomalies that often occur during market holidays.

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

## 3. The Visualization Layer (`dashboard/`)

This is where raw numbers are transformed into **Market Intelligence**.

- **`fx_app.py`**: The main entry point. It contains both the analytical processing logic and the embedded CSS design system to ensure a single-file, portable UI.

### Technical Analysis (The "Numbers")
The dashboard calculates several specialized metrics on-the-fly:

-   **Returns Calculation:** We compare the most recent price against historical points (7 Days up to the full database history) to calculate percentage change.
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

## 5. Dynamic Architecture (Anti-Hardcoding)

Unlike basic dashboards, this platform is built with a **Configuration-Driven** approach. 

- **Discovery Logic**: Instead of hardcoding "USD/INR", the app scans the Supabase database on initialization to discover all unique currency pairs.
- **Smart Mapping**: It uses a fallback transformation engine to convert raw yfinance tickers (like `EURUSD=X`) into professional labels (`EUR/USD`) dynamically.
- **Scalability**: This architecture allows the platform to scale from 1 to 100+ currency pairs by simply updating the database, requiring zero additional code changes.

---

## 🏁 Summary for Collaborators

If you are joining this project, focus on `backend/fx_scheduler.py` if you want to change how data is saved, or `dashboard/fx_app.py` if you want to add new charts or technical indicators.
