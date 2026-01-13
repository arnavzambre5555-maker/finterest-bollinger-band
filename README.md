ML-Driven Trading System Using Bollinger-Based Features

KSHITIJ 2026 – FinStreet / AQUA Competition Submission

1. Objective

This repository implements a fully automated, machine-learning–driven trading system in strict accordance with the KSHITIJ 2026 FinStreet problem statement.

The system is designed to:

Learn from historical price data

Predict 5-day forward price direction

Convert predictions into systematic trading signals

Backtest the strategy chronologically

Produce a true forward prediction without future data leakage

No manual intervention is used at any stage.

2. End-to-End Pipeline

The implemented pipeline follows the mandated structure:

FYERS Market Data → Feature Engineering → ML Model → Signal Generation → Backtest → Forward Prediction

Each stage is deterministic, reproducible, and auditable.

3. Data Source and Constraints

Market Data Source: FYERS Official Market Data API

Instrument: Single NSE-listed equity (as per competition stock list)

Frequency: Daily OHLCV

Training Window:

1 November 2025 – 31 December 2025

External / alternative datasets: Not used

All data is fetched programmatically using the FYERS API.
No CSV imports or offline datasets are used.

4. Feature Engineering

Technical indicators are used only as model features, not as trading rules.

Computed features:

20-day Simple Moving Average (SMA)

Rolling Standard Deviation (STD)

Bollinger Band Upper and Lower

Percent_B

Bandwidth

No indicator thresholds are used for direct BUY or SELL decisions.

5. Machine Learning Model

Model Type: Supervised binary classification

Algorithm: Random Forest Classifier

Input Features:

Percent_B

Bandwidth

SMA

STD

Target Definition

The model predicts whether price will move up or down over the next 5 trading days.

Target = 1  if  Close[t+5] > Close[t]
Target = 0  otherwise


This explicitly satisfies the requirement to predict the next 5 trading days.

Training Protocol

Model trained only on data from Nov–Dec 2025

Model state is frozen on 31 Dec 2025

Trained model is persisted as trained_model.pkl

6. Trading Signal Generation

Trading signals are generated exclusively from ML probabilities:

BUY: Probability(Up) > 0.55

SELL: Probability(Up) < 0.45

HOLD: Otherwise

There are no rule-based Bollinger thresholds in the decision logic.

7. Backtesting Methodology

Chronological backtest on the training window

No look-ahead bias

No data leakage

Capital, position sizing, and P&L tracked systematically

Performance metrics computed:

Total Return

Sharpe Ratio

Maximum Drawdown

Win Rate

Trade Log

Outputs:

results_summary.json

trades_log.csv

8. Forward Prediction (Mandatory Requirement)

A true forward prediction is generated as follows:

Model is frozen on 31 December 2025

No January 2026 market data is accessed

The last available state (Dec 31) is used to forecast the next 5 trading days

Output is saved to:

predictions_jan_2026.json


This file contains:

Probability of upward movement

Probability of downward movement

Predicted direction

Explicit confirmation that no future data was used

9. Automation and Reproducibility

Single execution entry point: main.py

Fully automated pipeline

No notebooks required

No manual steps

Running main.py generates all mandatory outputs in one execution.

10. Repository Structure
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

11. Evaluation Notes

This is not a rule-based Bollinger Bands strategy

Bollinger indicators are used strictly as features

Machine learning is the sole decision engine

Forward prediction is genuinely out-of-sample

12. Disclaimer

This project is developed solely for academic and competition purposes under the KSHITIJ 2026 FinStreet challenge.
It does not constitute investment advice or a live trading recommendation.
