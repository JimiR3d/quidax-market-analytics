"""
Quidax Market Analytics – Streamlit Dashboard

Real-time Nigerian crypto market intelligence powered by Quidax public API.
Features the Market Pulse Index™ — a composite market health score.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

from quidax_api import (
    get_market_summary, compute_market_pulse,
    get_ticker, get_order_book, get_ohlcv, PAIRS
)


# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quidax Market Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    .pulse-card {
        background: linear-gradient(135deg, #0F2C4D 0%, #1A1A2E 100%);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        border: 2px solid #1ABC9C;
        margin-bottom: 1rem;
    }
    .pulse-score {
        font-size: 3.5rem;
        font-weight: 700;
        color: #1ABC9C;
        line-height: 1;
    }
    .pulse-label {
        font-size: 1.2rem;
        color: #ECF0F1;
        margin-top: 0.5rem;
    }
    .pulse-subtitle {
        color: #95A5A6;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }

    .metric-card {
        background: #1A1A2E;
        border: 1px solid #2D2D44;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #95A5A6;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .positive { color: #27AE60; }
    .negative { color: #E74C3C; }
</style>
""", unsafe_allow_html=True)


def render_pulse_gauge(pulse):
    """Create a gauge chart for Market Pulse."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pulse["score"],
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Market Pulse Index™", "font": {"size": 16, "color": "#ECF0F1"}},
        number={"font": {"size": 48, "color": "#1ABC9C"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#95A5A6"},
            "bar": {"color": "#1ABC9C"},
            "bgcolor": "#1A1A2E",
            "steps": [
                {"range": [0, 25], "color": "#E74C3C"},
                {"range": [25, 50], "color": "#F39C12"},
                {"range": [50, 75], "color": "#3498DB"},
                {"range": [75, 100], "color": "#27AE60"},
            ],
            "threshold": {
                "line": {"color": "#FFFFFF", "width": 2},
                "thickness": 0.75,
                "value": pulse["score"],
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="#0D1117",
        font={"color": "#ECF0F1", "family": "Inter"},
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def render_market_table(summary):
    """Render the market overview table."""
    df = pd.DataFrame(summary)
    if df.empty:
        st.warning("No market data available.")
        return

    df["pair"] = df["pair"].str.upper()
    df["change_display"] = df["change_24h_pct"].apply(
        lambda x: f"+{x:.2f}%" if x >= 0 else f"{x:.2f}%"
    )

    st.dataframe(
        df[["pair", "last_price", "bid", "ask", "spread_pct",
            "volume_24h", "change_display"]].rename(columns={
            "pair": "Pair",
            "last_price": "Last Price",
            "bid": "Bid",
            "ask": "Ask",
            "spread_pct": "Spread %",
            "volume_24h": "24h Volume",
            "change_display": "24h Change",
        }),
        use_container_width=True,
        hide_index=True,
    )


def render_candlestick(pair):
    """Fetch and render OHLCV candlestick chart."""
    try:
        ohlcv = get_ohlcv(pair, period=60, limit=48)  # 48 hours
        if not ohlcv:
            st.info(f"No candlestick data available for {pair.upper()}")
            return
    except Exception as e:
        st.error(f"Failed to fetch OHLCV data: {e}")
        return

    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
    )

    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="Price",
        increasing_line_color="#27AE60",
        decreasing_line_color="#E74C3C",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df["timestamp"], y=df["volume"],
        name="Volume",
        marker_color="#3498DB",
        opacity=0.5,
    ), row=2, col=1)

    fig.update_layout(
        title=f"{pair.upper()} — 1H Candles (48h)",
        template="plotly_dark",
        paper_bgcolor="#0D1117",
        plot_bgcolor="#1A1A2E",
        font=dict(family="Inter", color="#ECF0F1"),
        xaxis_rangeslider_visible=False,
        height=500,
        showlegend=False,
    )
    fig.update_yaxes(title_text="Price (₦)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)


def render_order_book_chart(pair):
    """Render order book depth chart."""
    try:
        book = get_order_book(pair, limit=30)
        if not book:
            return
    except Exception:
        return

    asks = book.get("asks", [])
    bids = book.get("bids", [])

    if not asks or not bids:
        st.info("Order book data unavailable.")
        return

    ask_prices = [float(a["price"]) for a in asks]
    ask_volumes = [float(a["volume"]) for a in asks]
    bid_prices = [float(b["price"]) for b in bids]
    bid_volumes = [float(b["volume"]) for b in bids]

    # Cumulative depth
    import numpy as np
    ask_cum = list(np.cumsum(ask_volumes))
    bid_cum = list(np.cumsum(bid_volumes[::-1]))[::-1]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bid_prices, y=bid_cum,
        fill="tozeroy", name="Bids",
        line=dict(color="#27AE60"), fillcolor="rgba(39, 174, 96, 0.2)",
    ))
    fig.add_trace(go.Scatter(
        x=ask_prices, y=ask_cum,
        fill="tozeroy", name="Asks",
        line=dict(color="#E74C3C"), fillcolor="rgba(231, 76, 60, 0.2)",
    ))

    fig.update_layout(
        title=f"{pair.upper()} Order Book Depth",
        template="plotly_dark",
        paper_bgcolor="#0D1117",
        plot_bgcolor="#1A1A2E",
        font=dict(family="Inter", color="#ECF0F1"),
        xaxis_title="Price (₦)",
        yaxis_title="Cumulative Volume",
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Main app ─────────────────────────────────────────────────────────
def main():
    st.title("📊 Quidax Market Analytics")
    st.caption("Real-time Nigerian crypto market intelligence · Powered by Quidax API")

    # Sidebar
    with st.sidebar:
        st.markdown("### Settings")
        selected_pair = st.selectbox(
            "Trading Pair",
            PAIRS,
            format_func=lambda x: x.upper(),
            index=0,
        )
        auto_refresh = st.toggle("Auto-refresh (60s)", value=False)
        st.markdown("---")
        st.markdown(
            "Built by [Jimi Aboderin](https://github.com/JimiR3d)  \n"
            "[Source Code](https://github.com/JimiR3d/quidax-market-analytics)"
        )

    # Fetch data
    try:
        with st.spinner("Fetching market data..."):
            summary = get_market_summary()
            pulse = compute_market_pulse(summary)
    except Exception as e:
        st.error(f"Failed to connect to Quidax API: {e}")
        st.info("The dashboard requires internet access to the Quidax public API.")
        return

    # Market Pulse section
    col1, col2 = st.columns([1, 2])

    with col1:
        st.plotly_chart(render_pulse_gauge(pulse), use_container_width=True)
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem;">
            <span style="color: #95A5A6; font-size: 0.8rem;">
                Spread: {pulse['components'].get('spread_health', 0)}/40 ·
                Volume: {pulse['components'].get('volume_distribution', 0)}/30 ·
                Momentum: {pulse['components'].get('momentum', 0)}/30
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # KPI cards
        details = pulse.get("details", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Active Pairs", details.get("active_pairs", 0))
        c2.metric("Avg Spread", f"{details.get('avg_spread_pct', 0):.2f}%")
        c3.metric("Avg 24h Change", f"{details.get('avg_change_24h', 0):.2f}%")
        c4.metric("Market Status", pulse.get("label", "—"))

        st.markdown("#### Market Overview")
        render_market_table(summary)

    # Pair detail section
    st.markdown("---")
    st.markdown(f"### {selected_pair.upper()} Analysis")

    tab1, tab2 = st.tabs(["📈 Price Chart", "📊 Order Book"])

    with tab1:
        render_candlestick(selected_pair)

    with tab2:
        render_order_book_chart(selected_pair)

    # Footer
    st.markdown("---")
    st.caption(
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · "
        "Data from Quidax public API · All prices in NGN"
    )

    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()


if __name__ == "__main__":
    main()
