# Quidax Market Analytics

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)

A public-facing analytics tool that pulls live market data from the Quidax public API and displays real-time crypto market intelligence for Nigerian Naira (NGN) trading pairs. Features price tracking, order book depth visualisation, volatility metrics, and an original "Market Pulse" composite score.

## Who this is for

Nigerian crypto traders, fintech analysts, Quidax users who want deeper market insight, and anyone interested in NGN-denominated crypto market data.

## Features

- **Live price tracking** — BTC/NGN, ETH/NGN, and USDT/NGN with 24h change
- **Order book depth** — bid/ask spread visualisation
- **7-day volatility** — rolling volatility metric for each trading pair
- **Market Pulse score** — an original composite metric combining spread, volume, and volatility to give a single health reading per pair

## Tech stack

- **Python** — core logic
- **Requests** — Quidax API integration
- **Pandas** — data processing
- **Streamlit** — interactive web dashboard
- **Plotly** — charts and visualisation

## How to run locally

```bash
# Clone the repo
git clone https://github.com/JimiR3d/quidax-market-analytics.git
cd quidax-market-analytics

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The app opens at `http://localhost:8501` with live data from Quidax.

## Quidax API

This tool uses the [Quidax public API](https://www.quidax.com/api/v1/) — no authentication required.

| Endpoint | Purpose |
|----------|---------|
| `GET /markets` | List all available markets |
| `GET /markets/{market}/tickers` | Ticker data (price, volume, change) |
| `GET /markets/{market}/order_book` | Order book (bids and asks) |

## Live demo

_Coming soon — will be deployed to Streamlit Community Cloud._

## Project structure

```
quidax-market-analytics/
├── app.py                  # Main Streamlit app
├── api.py                  # Quidax API wrapper functions
├── metrics.py              # Market pulse score computation
├── requirements.txt
└── README.md
```

## Why I built this

I built this to demonstrate that I can take a public API, extract meaningful analytical value from it, and present it in a tool that's genuinely useful — not just a code exercise. The Market Pulse score is original thinking: a composite metric I designed to distill multiple market health signals into a single actionable number.

Built by [Jimi Aboderin](https://github.com/JimiR3d).

## License

MIT
