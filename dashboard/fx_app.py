import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import numpy as np
import sys
import os

# Ensure project root is in path for backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.news_fetcher import get_processed_news


# ─── Ticker Mapping Layer ──────────────────────────────────────────────────
TICKER_MAP = {
    "USDINR=X": "USD/INR",
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY",
    "DX-Y.NYB": "US Dollar Index (DXY)"
}
REVERSE_TICKER_MAP = {v: k for k, v in TICKER_MAP.items()}

EXPLANATIONS = {
    "USD/INR": "USD/INR shows how many Indian Rupees are required to buy 1 US Dollar. If it rises, the Dollar is strengthening. If it falls, the INR is strengthening.",
    "EUR/USD": "EUR/USD shows how many US Dollars are required to buy 1 Euro. If it rises, the Euro is strengthening. If it falls, the Dollar is strengthening.",
    "GBP/USD": "GBP/USD (The Cable) shows how many US Dollars buy 1 British Pound. If it rises, the Pound is strengthening.",
    "USD/JPY": "USD/JPY shows how many Japanese Yen buy 1 US Dollar. If it rises, the Dollar is strengthening vs the Yen.",
    "US Dollar Index (DXY)": "The DXY measures the value of the US Dollar against a basket of six foreign currencies. Higher DXY indicates broad USD strength."
}

# ─── Config ───────────────────────────────────────────────────────────────────
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PAGE_SIZE = 1000

st.set_page_config(
    page_title="FX Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💹"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background: #0b0f19; }
section[data-testid="stSidebar"] { background: #0d1117 !important; border-right: 1px solid #21262d; }

/* Sidebar Header */
.sidebar-header {
    padding: 0px 0 15px 0;
    text-align: left;
}
.sidebar-logo {
    font-size: 3.5rem;
    line-height: 1;
    margin-bottom: 8px;
}
.forex-title {
    font-size: 22px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #e6edf3;
    line-height: 1.1;
}
.intelligence-subtitle {
    font-size: 13px;
    color: #8b949e;
    letter-spacing: 0.03em;
}

/* Balanced Sidebar Spacing */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    gap: 0.8rem !important;
}
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
    margin-bottom: 0px;
}



/* Custom Snapshot Card */
.snapshot-card {
    background: linear-gradient(135deg, #161b27 0%, #1a2035 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.snapshot-left { display: flex; flex-direction: column; }
.snapshot-right { display: flex; gap: 30px; align-items: center; }
.pair-name { color: #8b949e; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 5px; }
.current-price { color: #e6edf3; font-size: 2.2rem; font-weight: 700; line-height: 1; }
.return-item { display: flex; flex-direction: column; align-items: flex-end; }
.return-label { color: #8b949e; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 2px; }
.return-value { font-size: 1.25rem; font-weight: 600; }

/* Volatility Card */
.vol-card {
    background: #161b27;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 10px;
}
.vol-header { color: #8b949e; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 8px; }
.vol-value-big { color: #e6edf3; font-size: 1.5rem; font-weight: 700; }

/* Explanation Box */
.explain-box {
    background: rgba(88, 166, 255, 0.05);
    border: 1px solid rgba(88, 166, 255, 0.2);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
    font-size: 0.9rem;
    color: #c9d1d9;
}

.tag-pos { color: #3fb950; }
.tag-neg { color: #f85149; }
/* Global Section Headers */
.section-header {
    color: #e6edf3;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-header span {
    font-size: 1.2rem;
    background: rgba(88, 166, 255, 0.1);
    color: #58a6ff;
    padding: 6px 14px;
    border-radius: 8px;
    font-weight: 500;
}

/* News Section Cards */
.news-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
    margin-top: 0.5rem;
}
.news-card {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.2s ease-in-out;
    display: flex;
    flex-direction: column;
    height: 100%;
}
.news-card:hover {
    border-color: #58a6ff;
    background: #161b22;
}
.news-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.news-badge {
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge-pos { background: rgba(46, 160, 67, 0.15); color: #3fb950; border: 1px solid rgba(46, 160, 67, 0.3); }
.badge-neg { background: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.3); }
.badge-neu { background: rgba(139, 148, 158, 0.15); color: #8b949e; border: 1px solid rgba(139, 148, 158, 0.3); }

.news-currency {
    color: #58a6ff;
    font-weight: 600;
    font-size: 0.7rem;
    letter-spacing: 0.05em;
}
.news-title {
    color: #f0f6fc;
    font-size: 1.05rem;
    font-weight: 600;
    margin: 8px 0 12px 0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.news-summary {
    color: #8b949e;
    font-size: 0.85rem;
    flex-grow: 1;
    line-height: 1.5;
    margin-bottom: 1rem;
}
.news-footer {
    padding-top: 12px;
    border-top: 1px solid #21262d;
    font-size: 0.75rem;
    color: #7d8590;
    display: flex;
    justify-content: space-between;
}
.news-link {
    color: #58a6ff;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 500;
}
.news-link:hover {
    text-decoration: underline;
}

</style>
""", unsafe_allow_html=True)

COLORS = ["#58a6ff", "#f0883e", "#3fb950", "#ff7b72", "#d2a8ff"]

# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner="Loading FX data…")
def load_all_data() -> pd.DataFrame:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Range-Unit": "items",
    }
    all_rows = []
    offset = 0
    while True:
        headers["Range"] = f"{offset}-{offset + PAGE_SIZE - 1}"
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/fx_rates?select=timestamp,pair,close&order=timestamp.desc",
            headers=headers,
            timeout=30,
        )

        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        all_rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["close"] = df["close"].astype(float)
    return df

# ─── Analytics helpers ────────────────────────────────────────────────────────
def filter_window(df: pd.DataFrame, days: int) -> pd.DataFrame:
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
    return df[df["timestamp"] >= cutoff].copy()

def compute_returns(s: pd.Series) -> dict:
    last = s.iloc[-1]
    def ret(n):
        if len(s) > n:
            return (last - s.iloc[-n]) / s.iloc[-n] * 100
        return None
    return {"1D": ret(2), "7D": ret(7), "30D": ret(30), "90D": ret(90), "1Y": ret(252)}

def compute_drawdown_stats(s: pd.Series, ts: pd.Series):
    peak = s.cummax()
    dd = (s - peak) / peak * 100
    max_dd = dd.min()
    max_dd_idx = dd.idxmin()
    max_dd_date = ts.iloc[dd.reset_index(drop=True).values.argmin()]
    peak_idx = peak[:max_dd_idx].idxmax() if len(peak[:max_dd_idx]) else max_dd_idx
    recovery = s[max_dd_idx:]
    peak_val = s[peak_idx]
    recovered = recovery[recovery >= peak_val]
    if not recovered.empty:
        rec_date = ts.iloc[s.index.get_loc(recovered.index[0])]
        peak_date = ts.iloc[s.index.get_loc(peak_idx)]
        duration = (rec_date - peak_date).days
    else:
        peak_date = ts.iloc[s.index.get_loc(peak_idx)]
        duration = (ts.iloc[-1] - peak_date).days
    return dd, max_dd, max_dd_date, duration

def rolling_vol_series(s: pd.Series, window=30) -> pd.Series:
    return s.pct_change().rolling(window, min_periods=5).std() * np.sqrt(252) * 100

# ─── Load Data ────────────────────────────────────────────────────────────────
try:
    df_all = load_all_data()
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

if df_all.empty:
    st.error("No data. Run the ingestion script first.")
    st.stop()

# Filter out pairs not in our mapping
df_all = df_all[df_all["pair"].isin(TICKER_MAP.keys())]

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # 🎨 Sidebar Title Redesign
    st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-logo">💹</div>
            <div class="forex-title">FOREX</div>
            <div class="intelligence-subtitle">Intelligence</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # 🏷 Sidebar Controls with Mapped Labels
    available_labels = [TICKER_MAP[t] for t in TICKER_MAP.keys() if t in df_all["pair"].unique()]
    
    selected_labels = st.multiselect(
        "Currency Pairs", available_labels,
        default=["USD/INR"], max_selections=4,
        help="ℹ️ Selection Guide:\n\n" + "\n\n".join([f"• **{k}**: {v}" for k,v in EXPLANATIONS.items()])
    )
    
    # Internal Ticker Conversion
    selected_pairs = [REVERSE_TICKER_MAP[label] for label in selected_labels]

    window_map = {"30D": 30, "90D": 90, "180D": 180, "1Y": 365, "3Y": 1095}
    window_label = st.select_slider("History Window", options=list(window_map.keys()), value="90D")
    window_days = window_map[window_label]

    normalize = st.toggle("Normalize to Base 100", value=False)
    show_ma20 = st.checkbox("Show 20-Day MA", value=True)
    show_ma50 = st.checkbox("Show 50-Day MA", value=True)

    st.caption(f"Last record: {df_all['timestamp'].max().strftime('%d %b %Y')}")
    
    st.markdown("---")
    st.markdown("### 📰 News Filters")
    news_count = st.slider("Max Articles", 3, 12, 6)
    
    # Currency filtering for news
    currency_options = ["Global", "USD", "EUR", "INR", "JPY", "GBP"]
    selected_news_currencies = st.multiselect(
        "Focus Hub",
        currency_options,
        default=["Global", "USD", "INR"],
        help="Select currencies you want to track news for."
    )
    
    if st.button("Refresh Feed", use_container_width=True):
        st.cache_data.clear()
        st.rerun()



if not selected_pairs:
    st.info("👈 Select at least one currency pair.")
    st.stop()

df_window = filter_window(df_all, window_days)
df_window = df_window[df_window["pair"].isin(selected_pairs)]

# ─── Page Header ──────────────────────────────────────────────────────────────
st.markdown("## 💹 FOREX Analytics Dashboard")
st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
# BLOCK 1 — MARKET SNAPSHOT
# ═══════════════════════════════════════════════════════════════════════
st.markdown("### 📍 Market Snapshot")

for pair in selected_pairs:
    label = TICKER_MAP[pair]
    pdf = df_all[df_all["pair"] == pair].sort_values("timestamp")
    if pdf.empty: continue
    rets = compute_returns(pdf["close"])
    last_price = pdf["close"].iloc[-1]
    
    def get_fmt(v):
        if v is None: return "N/A", "tag-neu"
        return f"{v:+.2f}%", "tag-pos" if v >= 0 else "tag-neg"

    r1d, c1d = get_fmt(rets.get("1D"))
    r7d, c7d = get_fmt(rets.get("7D"))
    r30d, c30d = get_fmt(rets.get("30D"))
    r90d, c90d = get_fmt(rets.get("90D"))

    st.markdown(f"""
    <div class="snapshot-card">
        <div class="snapshot-left">
            <div class="pair-name">{label}</div>
            <div class="current-price">{last_price:,.4f}</div>
        </div>
        <div class="snapshot-right">
            <div class="return-item"><div class="return-label">1D</div><div class="return-value {c1d}">{r1d}</div></div>
            <div class="return-item"><div class="return-label">7D</div><div class="return-value {c7d}">{r7d}</div></div>
            <div class="return-item"><div class="return-label">30D</div><div class="return-value {c30d}">{r30d}</div></div>
            <div class="return-item"><div class="return-label">90D</div><div class="return-value {c90d}">{r90d}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
# BLOCK 2 — TREND ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"### 📈 Trend Analysis — {window_label}")

fig_trend = go.Figure()

for i, pair in enumerate(selected_pairs):
    label = TICKER_MAP[pair]
    pdf_full = df_all[df_all["pair"] == pair].sort_values("timestamp").reset_index(drop=True)
    pdf_win = df_window[df_window["pair"] == pair].sort_values("timestamp").reset_index(drop=True)
    if pdf_win.empty: continue

    c = COLORS[i % len(COLORS)]
    y = pdf_win["close"].values.copy()
    
    if normalize and y.size > 0 and y[0] != 0:
        scale = y[0]
        y = (y / scale) * 100
        pdf_full["ma_base"] = (pdf_full["close"] / pdf_full["close"].iloc[0]) * 100
    else:
        pdf_full["ma_base"] = pdf_full["close"]

    fig_trend.add_trace(go.Scatter(x=pdf_win["timestamp"], y=y, name=label, mode="lines", line=dict(color=c, width=2)))

    if show_ma20:
        ma20 = pdf_full["ma_base"].rolling(20, min_periods=1).mean()
        mask = pdf_full["timestamp"] >= pdf_win["timestamp"].iloc[0]
        fig_trend.add_trace(go.Scatter(x=pdf_full["timestamp"][mask], y=ma20[mask], name=f"{label} 20MA", mode="lines", line=dict(color=c, width=1, dash="dot"), opacity=0.6, showlegend=False))
    
    if show_ma50:
        ma50 = pdf_full["ma_base"].rolling(50, min_periods=1).mean()
        mask = pdf_full["timestamp"] >= pdf_win["timestamp"].iloc[0]
        fig_trend.add_trace(go.Scatter(x=pdf_full["timestamp"][mask], y=ma50[mask], name=f"{label} 50MA", mode="lines", line=dict(color=c, width=1, dash="dash"), opacity=0.4, showlegend=False))

fig_trend.update_layout(template="plotly_dark", paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", height=450, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig_trend, use_container_width=True)

# Technical Explanation
st.markdown("""
<div class="explain-box">
    <b>Understanding Moving Averages (MA)</b><br>
    • <b>20-Day MA:</b> Reacts quickly to recent changes and helps visualize short-term direction.<br>
    • <b>50-Day MA:</b> Highlights the broader medium-term trend.<br>
    <b>When the price stays above these averages, the trend is generally upward.</b>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
# BLOCK 3 — VOLATILITY
# ═══════════════════════════════════════════════════════════════════════
st.markdown("### 🛡️ Volatility Metrics")
vol_cols = st.columns(len(selected_pairs))

for i, pair in enumerate(selected_pairs):
    label = TICKER_MAP[pair]
    pdf_full = df_all[df_all["pair"] == pair].sort_values("timestamp").reset_index(drop=True)
    if len(pdf_full) < 10: continue
    
    pct = pdf_full["close"].pct_change().dropna()
    cur_vol = pct.rolling(30, min_periods=5).std().iloc[-1] * np.sqrt(252) * 100
    vol_series = rolling_vol_series(pdf_full["close"], 30)
    hist_avg = vol_series.iloc[-504:].mean() if len(vol_series) >= 504 else vol_series.mean()
    
    with vol_cols[i]:
        st.markdown(f"""
        <div class="vol-card">
            <div class="vol-header">{label} - 30D Ann. Vol</div>
            <div class="vol-value-big">{cur_vol:.2f}%</div>
            <div style="font-size:0.8rem; color:#8b949e; margin-top:5px;">
                2Y Average: {hist_avg:.2f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# BLOCK 6 — MARKET INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header">🧠 Market Intelligence <span>AI-Powered</span></div>', unsafe_allow_html=True)

@st.cache_data(ttl=900) # Reduced TTL for troubleshooting
def load_news_data(currencies=None):
    try:
        # Pass currencies to get targeted news
        news = get_processed_news(query="forex OR \"exchange rate\"", page_size=50, currencies=currencies)
        if not news and currencies:
            # Fallback to global news if targeted news is empty
            print(f"No news found for {currencies}, falling back to global...")
            news = get_processed_news(query="forex OR \"exchange rate\"", page_size=30, currencies=None)
        return news
    except Exception as e:
        print(f"ERROR in load_news_data: {e}")
        # Final fallback - try one last time with basic query
        try:
             return get_processed_news(query="forex", page_size=20, currencies=None)
        except:
             return []

# Force refresh if requested via a trick (or just use standard cache)
all_news = load_news_data(tuple(selected_news_currencies) if selected_news_currencies else None)



if all_news:
    # Improved filtering logic
    if not selected_news_currencies:
        filtered_news = all_news[:news_count]
        st.info("Showing most recent global news.")
    else:
        # Normalize selections for comparison
        selections = [s.upper() for s in selected_news_currencies]
        filtered_news = []
        for item in all_news:
            curr = item.get("currency", "GLOBAL").upper()
            if curr in selections:
                filtered_news.append(item)
        
        # If we have specific results, use them
        if filtered_news:
            filtered_news = filtered_news[:news_count]
        else:
            # If NO results for specific currencies, inform user and show latest
            st.warning(f"No recent news found specifically for {', '.join(selected_news_currencies)}. Showing latest market updates instead.")
            filtered_news = all_news[:news_count]


    st.markdown('<div class="news-container">', unsafe_allow_html=True)
    for art in filtered_news:
        sentiment = art.get("sentiment", "Neutral")
        s_class = "badge-pos" if sentiment == "Positive" else "badge-neg" if sentiment == "Negative" else "badge-neu"
        currency = art.get("currency", "Global")
        pub_time = art.get("publishedAt", "")
        if pub_time:
            try:
                dt = datetime.fromisoformat(pub_time.replace("Z", "+00:00"))
                pub_time = dt.strftime("%H:%M · %b %d")
            except: pass
        
        source = art.get("source", {}).get("name", "Market")
        
        st.markdown(f"""
        <div class="news-card">
            <div class="news-meta">
                <span class="news-badge {s_class}">{sentiment}</span>
                <span class="news-currency">{currency}</span>
            </div>
            <div class="news-title">{art.get('title', 'Market Update')}</div>
            <div class="news-summary">{art.get('summary', '')}</div>
            <div class="news-footer">
                <b>{source}</b>
                <span>{pub_time}</span>
            </div>
            <a href="{art.get('url', '#')}" target="_blank" class="news-link" style="margin-top: 15px; display: block;">Read Full Analysis →</a>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Market feed currently unavailable.")



st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
# BLOCK 4 — DRAWDOWN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"### 📉 Drawdown Peak-to-Trough — {window_label}")

fig_dd = go.Figure()
dd_stats = []

for i, pair in enumerate(selected_pairs):
    label = TICKER_MAP[pair]
    pdf = df_window[df_window["pair"] == pair].sort_values("timestamp").reset_index(drop=True)
    if len(pdf) < 5: continue
    dd_series, max_dd, max_dd_date, duration = compute_drawdown_stats(pdf["close"], pdf["timestamp"])
    
    fig_dd.add_trace(go.Scatter(x=pdf["timestamp"], y=dd_series.values, name=label, mode="lines", fill="tozeroy", line=dict(color=COLORS[i % len(COLORS)], width=1.5)))
    dd_stats.append({"Pair": label, "Max DD": f"{max_dd:.2f}%", "Trough Date": max_dd_date.strftime("%d %b %Y"), "Duration": f"{int(duration)} days"})

fig_dd.update_layout(template="plotly_dark", paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", height=300, margin=dict(t=10, b=10))
st.plotly_chart(fig_dd, use_container_width=True)

if dd_stats:
    st.table(pd.DataFrame(dd_stats).set_index("Pair"))

# Explanation
st.markdown("""
<div class="explain-box">
    <b>Understanding Drawdown (Peak-to-Trough)</b>
    <ul>
        <li>Drawdown shows how much the currency has fallen from its most recent high.</li>
        <li><b>Formula:</b> (Current Price − Recent Peak Price) ÷ Recent Peak Price</li>
        <li><b>Trough Date:</b> The date when this decline reached its maximum level.</li>
        <li><b>Duration:</b> The number of days the currency remained below its previous peak before recovering (or until today if it has not yet recovered).</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# BLOCK 5 — DATA ENGINEERING AUDIT
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 📂 Data Engineering Audit")
cov_cols = st.columns(len(selected_pairs))

for idx, pair in enumerate(selected_pairs):
    label = TICKER_MAP[pair]
    pdf = df_all[df_all["pair"] == pair].sort_values("timestamp")
    if pdf.empty: continue
    ts = pdf["timestamp"]
    with cov_cols[idx]:
        st.markdown(f"""
        <div style="background:#161b27; border:1px solid #30363d; border-radius:8px; padding:15px; font-size:0.85rem;">
            <b>{label}</b><br>
            Records: {len(pdf):,}<br>
            Range: {ts.min().strftime("%b %Y")} - {ts.max().strftime("%b %Y")}<br>
            Source: Yahoo Finance
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Daily Currency Intelligence Platform · Powered by yfinance and Supabase")
