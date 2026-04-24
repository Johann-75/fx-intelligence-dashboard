# 💹 FX Intelligence Dashboard

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3EC988?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)

A premium, localized Forex Analytics platform designed for high-density technical analysis and risk assessment. Specialized for the **USD/INR** pair with global currency context.

---

## ✨ Key Features

- **📍 Real-Time Market Snapshot:** Instant access to current rates and multi-window returns (7D to ALL history).
- **📈 Professional Trend Analysis:** Interactive technical charts with 20-Day and 50-Day Moving Averages.
- **🛡️ Risk & Volatility Metrics:** Annualized 30D volatility tracking and Peak-to-Trough drawdown analysis.
- **📂 Reliable Data Pipeline:** Automated synchronization from Yahoo Finance to a managed Supabase instance.
- **🎨 Premium UI/UX:** A minimal, high-contrast dark theme designed for distraction-free analysis.

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (Python-based interactive web framework)
- **Backend:** [YFinance](https://github.com/ranaroussi/yfinance) (Market data extraction)
- **Database:** [Supabase](https://supabase.com/) (Managed PostgreSQL for time-series persistence)
- **Visualization:** [Plotly](https://plotly.com/) (High-performance financial charting)

## 🚀 Quick Start

1. **Environment Setup:**
   - Create a `.env` file in the root directory:
     ```env
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_anon_key
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. **Run Analysis:**
   - **One-Click (Windows):** Double-click `run_dashboard.bat`
   - **Manual:** `streamlit run dashboard/fx_app.py`

3. **Data Updates:**
   - **One-Click (Windows):** Double-click `sync_data.bat`
   - **Manual:** `python backend/fx_scheduler.py --period 1mo`

## 📂 Project Structure
```text
├── backend/            # Data ingestion and scheduled sync logic
├── dashboard/          # Streamlit UI and analytical transforms
│   └── fx_app.py       # Main dashboard logic (with embedded CSS)
├── .env                # Sensitive credentials (ignored by git)
├── README.md           # Project overview
├── EXPLANATION.md      # Detailed technical deep-dive
├── requirements.txt    # Standardized dependency list
├── run_dashboard.bat   # Windows shortcut to launch app
└── sync_data.bat      # Windows shortcut to sync data
```
