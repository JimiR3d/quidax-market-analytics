"""charts.py — Plotly chart functions for the Quidax Market Analytics dashboard.

Separated from app.py for modularity and testability.
All functions return plotly.graph_objects.Figure instances.
"""

import plotly.graph_objects as go
import pandas as pd


def create_candlestick_chart(trades_data: list, market: str) -> go.Figure:
    """Create a candlestick chart from recent trade data.

    Args:
        trades_data: List of trade dicts from the Quidax API.
        market: Market pair string (e.g., 'btcngn').

    Returns:
        A Plotly Figure with OHLC candlesticks.
    """
    if not trades_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No trade data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#888")
        )
        return fig

    df = pd.DataFrame(trades_data)
    df["price"] = pd.to_numeric(df.get("price", 0), errors="coerce")
    df["volume"] = pd.to_numeric(df.get("volume", 0), errors="coerce")
    df["created_at"] = pd.to_datetime(df.get("created_at", ""), errors="coerce")
    df = df.dropna(subset=["price", "created_at"])
    df = df.sort_values("created_at")

    # Resample into 15-minute OHLC bars
    df = df.set_index("created_at")
    ohlc = df["price"].resample("15min").ohlc().dropna()

    if ohlc.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for candlestick chart",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
        )
        return fig

    fig = go.Figure(data=[
        go.Candlestick(
            x=ohlc.index,
            open=ohlc["open"],
            high=ohlc["high"],
            low=ohlc["low"],
            close=ohlc["close"],
            increasing_line_color="#00D4AA",
            decreasing_line_color="#FF6B6B",
        )
    ])

    fig.update_layout(
        title=f"{market.upper()} — 15-Minute Candlestick",
        xaxis_title="Time",
        yaxis_title="Price (NGN)",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=420,
    )
    return fig


def create_order_book_chart(order_book: dict, market: str) -> go.Figure:
    """Create a depth chart from order book bid/ask data.

    Args:
        order_book: Dict with 'bids' and 'asks' lists.
        market: Market pair string.

    Returns:
        A Plotly Figure showing bid/ask depth.
    """
    fig = go.Figure()

    bids = order_book.get("bids", []) or []
    asks = order_book.get("asks", []) or []

    if bids:
        bid_prices = [float(b[0]) for b in bids[:30]]
        bid_volumes = [float(b[1]) for b in bids[:30]]
        # Cumulative volume
        bid_cum = []
        total = 0
        for v in bid_volumes:
            total += v
            bid_cum.append(total)

        fig.add_trace(go.Scatter(
            x=bid_prices, y=bid_cum,
            fill="tozeroy", fillcolor="rgba(0, 212, 170, 0.2)",
            line=dict(color="#00D4AA", width=2),
            name="Bids",
        ))

    if asks:
        ask_prices = [float(a[0]) for a in asks[:30]]
        ask_volumes = [float(a[1]) for a in asks[:30]]
        ask_cum = []
        total = 0
        for v in ask_volumes:
            total += v
            ask_cum.append(total)

        fig.add_trace(go.Scatter(
            x=ask_prices, y=ask_cum,
            fill="tozeroy", fillcolor="rgba(255, 107, 107, 0.2)",
            line=dict(color="#FF6B6B", width=2),
            name="Asks",
        ))

    fig.update_layout(
        title=f"{market.upper()} — Order Book Depth",
        xaxis_title="Price (NGN)",
        yaxis_title="Cumulative Volume",
        template="plotly_dark",
        height=380,
    )
    return fig


def create_volume_bar_chart(tickers: dict) -> go.Figure:
    """Create a horizontal bar chart of 24h trading volume by market.

    Args:
        tickers: Dict mapping market names to ticker data.

    Returns:
        A Plotly Figure with volume bars.
    """
    if not tickers:
        fig = go.Figure()
        fig.add_annotation(
            text="No ticker data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
        )
        return fig

    markets = []
    volumes = []
    for market, data in tickers.items():
        vol = float(data.get("volume", 0) or 0)
        if vol > 0:
            markets.append(market.upper())
            volumes.append(vol)

    # Sort by volume
    sorted_pairs = sorted(zip(volumes, markets), reverse=True)
    volumes, markets = zip(*sorted_pairs) if sorted_pairs else ([], [])

    fig = go.Figure(data=[
        go.Bar(
            x=list(volumes)[:10],
            y=list(markets)[:10],
            orientation="h",
            marker_color="#00D4AA",
        )
    ])

    fig.update_layout(
        title="Top Markets by 24h Volume",
        xaxis_title="Volume",
        template="plotly_dark",
        height=350,
        yaxis=dict(autorange="reversed"),
    )
    return fig
