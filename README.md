# Bollinger Bands Trading Strategy  
**IIT Kharagpur – KSHITIJ 2026 | AQUA Competition**

---

## Overview
Deterministic, walk-forward trading system implementing a Bollinger Bands mean-reversion strategy for NSE equities. Signals are generated at day *t* close and executed at day *t+1* open. No look-ahead bias. Fully reproducible.

---

## Strategy Logic

### Bollinger Bands (Base Strategy)
- 20-period SMA  
- ±2 standard deviations  
- Buy: Percent_B < 0.10  
- Sell: Percent_B > 0.90  

### Machine Learning Filter
- Predicts next-day direction (UP / DOWN)  
- Trained using walk-forward validation  
- Filters Bollinger signals only (does not replace them)

---

## Execution & Risk
- Position size: 95% of capital  
- Single position only  
- No leverage  
- Execution at next-day open  

---

## Backtesting Methodology
- Walk-forward evaluation (train ≤ *t*, predict *t+1*)  
- Signals generated at close of day *t*  
- Trades executed at open of day *t+1*  
- Strict chronological processing  

---

## Project Structure
submission/
├─ strategy/
│ ├─ bollinger.py
│ ├─ ml_filter.py
│ └─ fyers_api.py
├─ backtest/
│ └─ backtest_engine.py
├─ docs/
│ └─ STRATEGY_EXPLANATION.md
├─ main.py
└─ README.md

---

## Requirements
- Python 3.7+
- pandas
- numpy
- scikit-learn
- fyers-apiv3

pip install -r requirements.txt

---

## Usage

### Primary Mode (FYERS API)
Create `config.py` (not committed):

FYERS_CLIENT_ID = "YOUR_CLIENT_ID"
FYERS_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
FYERS_MODE = "dry_run" # or "live"

makefile
Copy code

Run:
python main.py --stock SONATSOFTW

---

## Performance Summary
**Instrument:** Sonata Software  
**Period:** Nov 3 – Dec 31, 2025  

- Total Return: 6.08%  
- Sharpe Ratio: 3.39  
- Max Drawdown: 1.33%  
- Win Rate: 100%  
- Trades: 2  

---

## Competition Compliance
- Sharpe Ratio > 1.5  
- Walk-forward backtesting  
- No look-ahead bias  
- Deterministic execution  
- FYERS API integration  

---

## Notes
- No credentials committed  
- No synthetic data  
- Historical backtest only  

---

## License
Educational use only. Developed for IIT Kharagpur – KSHITIJ 2026 | AQUA Competition.
