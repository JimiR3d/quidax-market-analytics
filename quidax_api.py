"""
Quidax API Wrapper

Clean Python interface for the Quidax public market data API.
Covers tickers, order books, trades, and OHLCV candles.

Docs: https://docs.quidax.com
"""

import requests
from datetime import datetime, timedelta
import time


BASE_URL = "https://www.quidax.com/api/v1"

# Supported trading pairs on Quidax
PAIRS = [
    "btcngn", "ethngn", "usdtngn", "usdcngn",
    "xrpngn", "bnbngn", "solngn", "trxngn",
    "btcusdt", "ethusdt",
]


class QuidaxAPIError(Exception):
    """Raised when the Quidax API returns an error."""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Quidax API Error {status_code}: {message}")


def _get(endpoint, params=None):
    """Make a GET request to the Quidax API."""
    url = f"{BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            raise QuidaxAPIError(resp.status_code, resp.text[:200])
        data = resp.json()
        return data.get("data", data)
    except requests.exceptions.ConnectionError:
        raise QuidaxAPIError(0, "Connection failed. Check internet connection.")
    except requests.exceptions.Timeout:
        raise QuidaxAPIError(0, "Request timed out.")


def get_ticker(pair="btcngn"):
    """
    Get current ticker data for a trading pair.

    Returns: dict with buy, sell, low, high, last, vol, etc.
    """
    return _get(f"/markets/tickers/{pair}")


def get_all_tickers():
    """
    Get ticker data for all trading pairs.

    Returns: list of ticker dicts
    """
    return _get("/markets/tickers")


def get_order_book(pair="btcngn", limit=20):
    """
    Get the current order book for a trading pair.

    Args:
        pair: Trading pair (e.g., 'btcngn')
        limit: Number of orders per side

    Returns: dict with 'asks' and 'bids' lists
    """
    return _get(f"/markets/{pair}/order_book", params={"limit": limit})


def get_recent_trades(pair="btcngn", limit=50):
    """
    Get recent trades for a trading pair.

    Args:
        pair: Trading pair
        limit: Number of trades to return

    Returns: list of trade dicts
    """
    return _get(f"/markets/{pair}/trades", params={"limit": limit})


def get_ohlcv(pair="btcngn", period=60, limit=100):
    """
    Get OHLCV candlestick data.

    Args:
        pair: Trading pair
        period: Candle period in minutes (1, 5, 15, 30, 60, 120, 240, 720, 1440)
        limit: Number of candles

    Returns: list of [timestamp, open, high, low, close, volume]
    """
    return _get(f"/markets/{pair}/k_line", params={
        "period": period,
        "limit": limit,
    })


def get_market_summary():
    """
    Get a summary of all markets with computed metrics.

    Returns: list of dicts with pair, price, volume, spread, change
    """
    tickers = get_all_tickers()
    summary = []

    for pair_id, ticker_data in tickers.items():
        ticker = ticker_data.get("ticker", {})
        try:
            last = float(ticker.get("last", 0))
            buy = float(ticker.get("buy", 0))
            sell = float(ticker.get("sell", 0))
            vol = float(ticker.get("vol", 0))
            high = float(ticker.get("high", 0))
            low = float(ticker.get("low", 0))
            open_price = float(ticker.get("open", 0))

            # Compute spread
            spread = sell - buy if buy > 0 and sell > 0 else 0
            spread_pct = (spread / buy * 100) if buy > 0 else 0

            # Compute 24h change
            change_pct = ((last - open_price) / open_price * 100) if open_price > 0 else 0

            # Compute intraday range
            intraday_range = high - low

            summary.append({
                "pair": pair_id,
                "last_price": last,
                "bid": buy,
                "ask": sell,
                "spread": round(spread, 2),
                "spread_pct": round(spread_pct, 4),
                "volume_24h": vol,
                "high_24h": high,
                "low_24h": low,
                "change_24h_pct": round(change_pct, 2),
                "intraday_range": round(intraday_range, 2),
            })
        except (ValueError, TypeError, ZeroDivisionError):
            continue

    return sorted(summary, key=lambda x: x["volume_24h"], reverse=True)


def compute_market_pulse(summary):
    """
    Compute the Market Pulse Index — a proprietary composite
    score indicating overall Quidax market activity.

    Components:
        - Weighted average spread (lower = healthier)
        - Volume concentration (HHI-inspired)
        - Average price momentum

    Returns: dict with pulse score (0-100) and components
    """
    if not summary:
        return {"score": 0, "label": "No Data", "components": {}}

    total_volume = sum(m["volume_24h"] for m in summary)
    if total_volume == 0:
        return {"score": 0, "label": "No Data", "components": {}}

    # 1. Spread Health (0-40 pts) — lower avg spread = healthier
    avg_spread = sum(m["spread_pct"] for m in summary) / len(summary)
    spread_score = max(0, 40 - avg_spread * 10)

    # 2. Volume Distribution (0-30 pts) — more distributed = healthier
    shares = [(m["volume_24h"] / total_volume) ** 2 for m in summary]
    hhi = sum(shares)
    volume_score = max(0, 30 * (1 - hhi))

    # 3. Momentum (0-30 pts) — positive avg change = bullish
    avg_change = sum(m["change_24h_pct"] for m in summary) / len(summary)
    momentum_score = min(30, max(0, 15 + avg_change * 3))

    pulse = round(spread_score + volume_score + momentum_score, 1)
    pulse = min(100, max(0, pulse))

    if pulse >= 75:
        label = "Strong"
    elif pulse >= 50:
        label = "Healthy"
    elif pulse >= 25:
        label = "Weak"
    else:
        label = "Critical"

    return {
        "score": pulse,
        "label": label,
        "components": {
            "spread_health": round(spread_score, 1),
            "volume_distribution": round(volume_score, 1),
            "momentum": round(momentum_score, 1),
        },
        "details": {
            "avg_spread_pct": round(avg_spread, 4),
            "hhi": round(hhi, 4),
            "avg_change_24h": round(avg_change, 2),
            "active_pairs": len(summary),
            "total_volume": round(total_volume, 2),
        },
    }
