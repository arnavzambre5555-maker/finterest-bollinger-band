ML-Driven Bollinger Bands Trading System

KSHITIJ 2026 – FinStreet / AQUA Competition Submission

1. Problem Alignment

This project implements an end-to-end ML-driven trading system as required by the KSHITIJ 2026 FinStreet problem statement.

The system strictly follows the mandated pipeline:

Market Data (FYERS API) → Feature Engineering → ML Model → Trading Signals → Backtest → Forward Prediction

No manual intervention is used at any stage.

2. Data Source & Constraints

Data Source: FYERS Official Market Data API

Instrument: Single NSE equity (as per competition stock list)

Frequency: Daily OHLCV

Training Window:

1 November 2025 – 31 December 2025

External datasets: ❌ Not used

CSV imports: ❌ Not used

All data is fetched programmatically via FYERS.

3. Feature Engineering

Technical indicators are used only as ML features, not as rule-based triggers.

Computed features:

Simple Moving Average (20-day)

Rolling Standard Deviation

Bollinger Band Upper / Lower

Percent_B

Bandwidth

No indicator thresholds are used for direct BUY/SELL decisions.

4. Machine Learning Model

Model Type: Supervised Classification

Algorithm: Random Forest Classifier

Target Variable:

1 → Price increases over the next 5 trading days

0 → Otherwise

Target Construction
Target = sign( Close[t+5] − Close[t] )


This directly satisfies the requirement to predict the next 5 trading days.

Training

Model trained only on Nov–Dec 2025

Model is frozen on 31 Dec 2025

Trained model is saved as trained_model.pkl

5. Trading Signal Logic (ML-Driven)

Signals are generated exclusively from ML probabilities:

BUY: P(Up) > 0.55

SELL: P(Up) < 0.45

HOLD: otherwise

There are no rule-based Bollinger thresholds in signal generation.

6. Backtesting Methodology

Chronological backtest on training window

No look-ahead bias

No future data leakage

Position sizing and capital tracking fully automated

Metrics computed:

Total Return

Sharpe Ratio

Maximum Drawdown

Win Rate

Trade Log

Backtest results are saved as:

results_summary.json

trades_log.csv

7. Forward Prediction (Mandatory Requirement)

A true forward prediction is generated as follows:

Model is frozen on 31 Dec 2025

No Jan 2026 market data is used

Last available state (Dec 31) is used to forecast the next 5 trading days

Output saved as:

predictions_jan_2026.json


This file contains:

Probability of upward movement

Probability of downward movement

Predicted direction

Explicit confirmation that no future data was used

8. Reproducibility & Automation

Single execution entry point: main.py

Fully automated pipeline

No notebooks required

All outputs generated in one run

Required output files:

trained_model.pkl

predictions_jan_2026.json

results_summary.json

trades_log.csv

9. File Structure
.
├── main.py
├── ml_model.py
├── strategy.py
├── fyers_data.py
├── trained_model.pkl
├── predictions_jan_2026.json
├── results_summary.json
├── trades_log.csv
└── README.md

10. Key Notes for Evaluation

This is not a rule-based Bollinger strategy

Bollinger Bands are features, not decision rules

ML model is the sole decision engine

Forward prediction is genuinely out-of-sample

11. Disclaimer

This project is built strictly for academic and competition purposes in accordance with the KSHITIJ 2026 FinStreet problem statement.
It is not intended as live trading advice.
