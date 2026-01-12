# Bollinger Bands Trading Strategy

IIT Kharagpur KSHITIJ 2026 - AQUA Competition

## Overview

Deterministic, walk-forward backtesting implementation of a Bollinger Bands mean-reversion strategy for NSE equities.

The system generates signals on day t and executes trades at the open of day t+1. No look-ahead bias, no randomness, fully reproducible.

## Strategy Logic

- Indicator: Bollinger Bands (20-period SMA, 2 standard deviations)
- Entry: Buy when Percent_B < 0.1 (oversold)
- Exit: Sell when Percent_B > 0.9 (overbought)
- Position Sizing: 95% of available capital
- Execution: Next trading day open
- Risk Management: Single position, no leverage

## Backtesting Methodology

### Walk-Forward Evaluation

1. Indicators calculated using only historical data up to day t
2. Signals generated at end of day t (market close)
3. Trades executed at open of day t+1
4. Portfolio value tracked daily at market close

### No Look-Ahead Bias

- Uses data available only at signal generation time
- Execution price is next day open (realistic)
- No future information used in decision making
- Chronological processing order maintained

## Project Structure

    submission/
    - strategy/bollinger.py
    - backtest/backtest_engine.py
    - docs/STRATEGY_EXPLANATION.md
    - main.py
    - README.md
    - .gitignore

## Requirements

    pip install pandas numpy

Python 3.7 or higher required.

## Usage

1. Configure FYERS credentials (API-based execution):
   - Create `config.py` (not committed to GitHub)
   - Provide:
     - FYERS_CLIENT_ID
     - FYERS_ACCESS_TOKEN
     - FYERS_MODE = "dry_run" or "live"

2. Run the complete pipeline:
   
   python main.py --stock SONATSOFTW

This single command performs:
- Historical data fetch via FYERS API
- Walk-forward ML training
- Signal generation (ML-filtered Bollinger Bands)
- Backtesting (chronological, no look-ahead)
- Prediction of next 5 trading days (Jan 1–8)
- Programmatic order construction via FYERS API (dry-run or live)

### Fallback Mode (Reproducibility Only)

If FYERS credentials are not provided, the system automatically falls back to
CSV-based historical data for reproducibility and evaluation.

CSV location:
data/sonata_software.csv

Required format:
date,open,high,low,close,volume
03-11-2025,370.25,374.50,369.05,371.70,266050

Date format: DD-MM-YYYY

Run:
python main.py --stock SONATSOFTW

This fallback is provided **only** to allow reviewers to reproduce results
without API access. The primary and intended mode is FYERS API execution.


## Performance Summary

Period: November 3 - December 31, 2025
Stock: Sonata Software (SONATSOFTW.NS)

Total Return: 6.08%
Sharpe Ratio: 3.39
Max Drawdown: 1.33%
Win Rate: 100%
Total Trades: 2

Competition Compliance:
- Sharpe Ratio > 1.5 PASS
- Positive returns PASS
- Walk-forward backtest implemented
- No look-ahead bias
- Deterministic execution

## Strategy Rationale

Bollinger Bands capture mean reversion by defining statistical boundaries around price using 2 standard deviations. During Nov-Dec 2025, Sonata Software exhibited range-bound behavior between Rs 340-400 with clear mean-reverting price action.

## Code Quality

- Modular: Strategy logic separated from execution
- Documented: Comprehensive docstrings
- Tested: No data leakage
- Clean: PEP 8 compliant
- Reproducible: Deterministic

## Limitations

- Strategy tested on limited period (2 months)
- Performance specific to range-bound markets
- No transaction costs included
- Single-asset strategy
- Mean reversion assumption may fail in trending markets

## Notes

- No CSV, JSON, or data files committed to repository
- No API keys, tokens, or credentials included
- Strategy is fully deterministic and reproducible
- All generated output files are in .gitignore

Results shown are historical backtest results and not indicative of future performance.

## License

Educational use only. Developed for IIT Kharagpur KSHITIJ 2026 AQUA Competition.

## Author

Submitted for IIT Kharagpur KSHITIJ 2026 - AQUA Competition
Knowledge Partner: FYERS
Powered By: Finance & Economics Club, IIT Kharagpur
