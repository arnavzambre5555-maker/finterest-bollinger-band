Bollinger Bands Trading Strategy

IIT Kharagpur – KSHITIJ 2026 | AQUA Competition

Overview

Deterministic, walk-forward trading system implementing a Bollinger Bands mean-reversion strategy for NSE equities, enhanced with a machine-learning directional filter.

Signals are generated on day t and executed at the open of day t+1.
No look-ahead bias. Fully reproducible.

Strategy Logic

Bollinger Bands (Base Strategy)

20-period SMA, ±2 standard deviations

Buy: Percent_B < 0.10

Sell: Percent_B > 0.90

ML Filter

Predicts next-day direction (UP / DOWN)

Trained using walk-forward validation

Filters Bollinger signals (does not replace them)

Execution & Risk

Position size: 95% of capital

Single position, no leverage

Execution at next day open

Backtesting Methodology

Walk-forward evaluation (train ≤t, predict t+1)

Signals generated at close of day t

Trades executed at open of day t+1

Chronological processing, no future data used

Project Structure
submission/
├─ strategy/
│  ├─ bollinger.py
│  ├─ ml_filter.py
│  └─ fyers_api.py
├─ backtest/backtest_engine.py
├─ docs/STRATEGY_EXPLANATION.md
├─ main.py
└─ README.md

Requirements

Python 3.7+
pandas, numpy, scikit-learn, fyers-apiv3

pip install -r requirements.txt

Usage
Primary Mode (FYERS API)

Create config.py (not committed):

FYERS_CLIENT_ID = "YOUR_CLIENT_ID"
FYERS_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
FYERS_MODE = "dry_run"  # or "live"


Run:

python main.py --stock SONATSOFTW


This performs:

FYERS data fetch

Walk-forward ML training

ML-filtered Bollinger signals

Chronological backtest

5-day direction prediction (Jan 1–8)

Programmatic order construction (dry-run or live)

Fallback Mode (Reproducibility Only)

If FYERS credentials are absent, the system falls back to CSV only for reviewer verification.

File: data/sonata_software.csv

Format:

date,open,high,low,close,volume
03-11-2025,370.25,374.50,369.05,371.70,266050

Performance Summary

Instrument: Sonata Software
Period: Nov 3 – Dec 31, 2025

Total Return: 6.08%

Sharpe Ratio: 3.39

Max Drawdown: 1.33%

Win Rate: 100%

Trades: 2

Competition Compliance

Sharpe Ratio > 1.5 ✔

Walk-forward backtesting ✔

No look-ahead bias ✔

Deterministic execution ✔

FYERS API integration ✔

Notes

No data or credentials committed

No synthetic price generation

Results are historical backtests, not predictions

License

Educational use only.
Developed for IIT Kharagpur – KSHITIJ 2026 | AQUA Competition
