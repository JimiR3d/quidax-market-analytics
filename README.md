# 📊 Quidax Market Analytics

Real-time Nigerian crypto market intelligence dashboard powered by the Quidax public API. Features the **Market Pulse Index™** — a proprietary composite score for market health.

---

## Architecture

```
quidax_api.py (API Wrapper)
    ├── get_ticker()          → Single pair data
    ├── get_all_tickers()     → All market tickers
    ├── get_order_book()      → Bid/ask depth
    ├── get_recent_trades()   → Trade history
    ├── get_ohlcv()           → Candlestick data
    ├── get_market_summary()  → Computed market overview
    └── compute_market_pulse()→ Market Pulse Index™
                    ↓
app.py (Streamlit Dashboard)
    ├── Market Pulse gauge
    ├── KPI cards
    ├── Market overview table
    ├── Candlestick charts (Plotly)
    └── Order book depth chart
```

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| API Client | requests | Quidax REST API integration |
| Dashboard | Streamlit | Interactive web UI |
| Charts | Plotly | Candlestick, gauge, depth charts |
| Data | Pandas, NumPy | Processing and aggregation |
| CI | GitHub Actions | Flake8 linting |

## Market Pulse Index™

A composite score (0-100) measuring overall Quidax market activity:

| Component | Weight | Measures |
|-----------|--------|----------|
| Spread Health | 0-40 pts | Avg bid-ask spread across pairs |
| Volume Distribution | 0-30 pts | HHI-inspired concentration metric |
| Momentum | 0-30 pts | Average 24h price change direction |

**Interpretation:**
- 🟢 75-100: **Strong** — Tight spreads, distributed volume, positive momentum
- 🔵 50-74: **Healthy** — Normal market conditions
- 🟡 25-49: **Weak** — Wide spreads or concentrated volume
- 🔴 0-24: **Critical** — Low liquidity, extreme spreads

## Key Features

### API Wrapper (`quidax_api.py`)
- Clean Python interface for all Quidax public endpoints
- Market summary with computed spread, change, and range metrics
- Error handling with custom `QuidaxAPIError` exception
- 10 supported trading pairs (BTC, ETH, USDT, USDC, XRP, BNB, SOL, TRX)

### Dashboard (`app.py`)
- **Market Pulse gauge** — Animated indicator with color-coded ranges
- **KPI cards** — Active pairs, avg spread, 24h change, market status
- **Market table** — All pairs with price, bid, ask, spread, volume, change
- **Candlestick charts** — 1H candles with volume subplot (48h window)
- **Order book depth** — Cumulative bid/ask visualization
- **Auto-refresh** — Optional 60s polling
- Dark theme, Inter font, professional styling

## Quick Start

```bash
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The dashboard opens at `http://localhost:8501` and fetches live data from Quidax.

## API Endpoints Used

| Endpoint | Method |
|----------|--------|
| `/markets/tickers` | `get_all_tickers()` |
| `/markets/tickers/{pair}` | `get_ticker(pair)` |
| `/markets/{pair}/order_book` | `get_order_book(pair)` |
| `/markets/{pair}/trades` | `get_recent_trades(pair)` |
| `/markets/{pair}/k_line` | `get_ohlcv(pair)` |

## Project Context

This project demonstrates:
- **API integration** — RESTful API consumption with error handling
- **Financial analytics** — Custom market health scoring (HHI, momentum)
- **Real-time dashboards** — Streamlit with auto-refresh and live data
- **Data visualization** — Professional candlestick, gauge, and depth charts

Built as part of my data analyst portfolio. Uses only Quidax public API — no authentication required.

## Author

**Jimi Aboderin**  
[LinkedIn](https://www.linkedin.com/in/oluwafolajinmi-aboderin-695848249/) · [GitHub](https://github.com/JimiR3d) · folajinmi13@gmail.com
