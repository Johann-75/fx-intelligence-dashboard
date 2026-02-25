# FOREX Intelligence Dashboard 💹

A professional, real-time Foreign Exchange analytics platform built with Streamlit and Supabase. Designed for Business Intelligence and Analytics (BIA) applications.

## 🚀 Key Features

*   **Real-time Data**: Fetches live and historical FX rates via `yfinance`.
*   **Trend Smoothing**: Visualizes **20-Day** and **50-Day Moving Averages** for short/medium-term trend identification.
*   **Risk Analysis**: Calculates 30-day annualized volatility compared against 2-year historical averages.
*   **Drawdown Measurement**: Tracks peak-to-trough losses, trough dates, and recovery durations.
*   **Relative Performance**: One-click normalization (Base 100) to compare multiple currency pairs (e.g., USD/INR vs. USD/JPY) on a single scale.
*   **Academic Design**: Includes on-screen technical explanations of all financial metrics.

## 📂 Project Structure

```text
├── backend/
│   ├── fx_fetcher.py   # Yahoo Finance data fetching engine
│   └── fx_scheduler.py # Supabase data ingestion & update logic
└── dashboard/
    └── fx_app.py       # Core Streamlit application (The Dashboard)
```

## 🛠 Tech Stack

*   **Logic**: Python (Pandas, Numpy, Requests)
*   **UI/UX**: Streamlit + Plotly (Custom Premium Dark Theme)
*   **Database**: Supabase (PostgreSQL)

## 🔧 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Johann-75/fx-intelligence-dashboard.git
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit pandas plotly yfinance python-dotenv requests numpy
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

4. **Initialize Data**:
   ```bash
   python backend/fx_scheduler.py --period 1y
   ```

5. **Run Dashboard**:
   ```bash
   streamlit run dashboard/fx_app.py
   ```
