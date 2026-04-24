import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import numpy as np

# ─── Ticker Mapping Layer ──────────────────────────────────────────────────
TICKER_MAP = {
    "USDINR=X": "USD/INR",
}
REVERSE_TICKER_MAP = {v: k for k, v in TICKER_MAP.items()}

EXPLANATIONS = {
    "USD/INR": "USD/INR shows how many Indian Rupees are required to buy 1 US Dollar. If it rises, the Dollar is strengthening (INR is weakening). If it falls, the INR is strengthening.",
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;700&display=swap');

/* Core Layout Overrides */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top right, #111827, #0b0f19) !important;
}

html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
    color: #e6edf3;
}
h1, h2, h3, .forex-title {
    font-family: 'Outfit', sans-serif !important;
}

/* Sidebar with deeper blur */
section[data-testid="stSidebar"] { 
    background: rgba(13, 17, 23, 0.7) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Premium Sidebar Header */
.sidebar-header {
    padding: 30px 0;
    text-align: left;
}
.sidebar-logo {
    font-size: 4.5rem;
    margin-bottom: 15px;
    filter: drop-shadow(0 0 15px rgba(88, 166, 255, 0.4));
}
.forex-title {
    font-size: 28px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    background: linear-gradient(90deg, #ffffff, #8b949e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Modern Snapshot Card - Restored Professional Layout */
.snapshot-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}
.snapshot-card:hover {
    border-color: rgba(88, 166, 255, 0.5);
    transform: translateY(-4px);
    background: rgba(255, 255, 255, 0.05);
}
.snapshot-left { display: flex; flex-direction: column; }
.snapshot-right { display: flex; gap: 40px; align-items: center; }
.pair-name { color: #8b949e; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.15em; font-weight: 600; margin-bottom: 10px; }
.current-price { 
    color: #ffffff; 
    font-size: 2.8rem; 
    font-weight: 700; 
    line-height: 1;
    font-family: 'Outfit', sans-serif;
    letter-spacing: -0.02em;
}
.return-item { display: flex; flex-direction: column; align-items: flex-end; }
.return-label { color: #7d8590; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 4px; font-weight: 500; }
.return-value { font-size: 1.4rem; font-weight: 700; font-family: 'Outfit', sans-serif; }

/* Status Colors & Glows */
.tag-pos { color: #00ffaa !important; text-shadow: 0 0 15px rgba(0, 255, 170, 0.4); }
.tag-neg { color: #ff4455 !important; text-shadow: 0 0 15px rgba(255, 68, 85, 0.4); }
.tag-neu { color: #8b949e; }

/* Metrics Grid Cards */
/* Bolder Volatility Metrics */
.vol-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.3s ease;
    text-align: left;
}
.vol-card:hover { 
    background: rgba(255, 255, 255, 0.06); 
    border-color: rgba(255, 255, 255, 0.2);
}
.vol-header { color: #8b949e; font-size: 0.9rem; text-transform: uppercase; margin-bottom: 15px; font-weight: 600; letter-spacing: 0.05em; }
.vol-value-big { 
    color: #ffffff; 
    font-size: 2.5rem; 
    font-weight: 700; 
    font-family: 'Outfit', sans-serif;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

.explain-box {
    background: rgba(88, 166, 255, 0.05);
    border-left: 5px solid #58a6ff;
    border-radius: 8px;
    padding: 24px;
    margin: 30px 0;
    color: #a1a1aa;
    line-height: 1.7;
    font-size: 1rem;
}

/* Section Dividers */
.section-header {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 700;
    margin: 50px 0 30px 0;
    font-family: 'Outfit', sans-serif;
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
            f"{SUPABASE_URL}/rest/v1/fx_rates?select=timestamp,pair,close&order=timestamp.asc",
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
    df_all  = load_all_data()
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
    # 🎨 Advanced CSS: Lock Scroll + Flex-Fill
    st.markdown("""
        <style>
            /* Disable Sidebar Scrolling */
            [data-testid="stSidebar"] > div:first-child {
                overflow: hidden !important;
            }
            /* Main Sidebar Container */
            .sidebar-wrapper {
                display: flex;
                flex-direction: column;
                height: 92vh; /* Use view height to fill screen */
                justify-content: space-between;
                padding-bottom: 20px;
            }
            .sidebar-top {
                flex-grow: 0;
            }
            .sidebar-middle {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 2rem;
            }
            .sidebar-bottom {
                flex-grow: 0;
                text-align: center;
                border-top: 1px solid rgba(255,255,255,0.05);
                padding-top: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    # 🏗️ Start Sidebar Structure
    st.markdown('<div class="sidebar-top">', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 3rem; filter: drop-shadow(0 0 10px rgba(0, 255, 127, 0.4));">💹</div>
            <h1 style="font-size: 2rem; font-weight: 900; letter-spacing: 2px; margin: 0; color: #fff;">FOREX</h1>
            <p style="font-size: 0.8rem; opacity: 0.5; letter-spacing: 3px; text-transform: uppercase;">Analysis</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-middle">', unsafe_allow_html=True)
    
    # 🏷️ Selection Logic (Dynamic)
    # Automatically identify available pairs from the database
    available_tickers = df_all["pair"].unique().tolist()
    available_labels = [TICKER_MAP.get(t, t.split('=')[0].replace('USD', 'USD/')) for t in available_tickers]
    
    selected_label = st.selectbox("Currency Pair", options=available_labels, index=0)
    selected_pairs = [t for t in available_tickers if TICKER_MAP.get(t, t.split('=')[0].replace('USD', 'USD/')) == selected_label]

    # 📅 Timeline
    window_map = {"7D": 7, "30D": 30, "90D": 90, "1Y": 365, "ALL": 9999}
    window_label = st.select_slider("History Window", options=list(window_map.keys()), value="90D")
    window_days = window_map[window_label]

    # 📊 Technicals
    with st.container():
        st.markdown("### 📊 Indicators")
        show_ma20 = st.checkbox("20D Moving Average", value=True)
        show_ma50 = st.checkbox("50D Moving Average", value=True)
        normalize = False
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ⚓ Footer
    st.markdown(f"""
        <div class="sidebar-bottom">
            <span style="opacity: 0.3; font-size: 0.75rem;">Last sync: {df_all['timestamp'].max().strftime('%d %b %Y')}</span>
        </div>
    """, unsafe_allow_html=True)


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

# 📈 TREND ANALYSIS
st.markdown(f"### 📈 Trend Analysis — {window_label}")

from plotly.subplots import make_subplots
fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

# ─── Indicators ───

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

fig_trend.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=500,
    hovermode="x unified",
    font=dict(family="Inter, sans-serif"),
    margin=dict(t=20, b=20, l=20, r=20),
    xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor="rgba(0,0,0,0)"
    )
)
st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

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

fig_dd.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=320,
    margin=dict(t=10, b=10, l=20, r=20),
    font=dict(family="Inter, sans-serif"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
)
st.plotly_chart(fig_dd, use_container_width=True, config={'displayModeBar': False})

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
