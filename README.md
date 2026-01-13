# Bollinger Bands Trading Strategy with Machine Learning

## IIT Kharagpur KSHITIJ 2026 - AQUA Competition Submission

### Overview
ML-enhanced mean reversion strategy combining Bollinger Bands with Logistic Regression for improved signal quality.

### Strategy Components

#### 1. Machine Learning Model
- **Algorithm**: Logistic Regression (scikit-learn)
- **Target**: Next-day price direction (up/down)
- **Features**:
  - Percent_B (position within Bollinger Bands)
  - Bollinger Bandwidth (volatility measure)
  - Distance from SMA (trend deviation)
  - 1-day return (momentum)
- **Training**: Walk-forward validation with fresh model instances (no look-ahead bias)
- **Output**: Probability of upward price movement

#### 2. Signal Generation Rules
- **BUY**: Bollinger oversold (Percent_B < 0.1) AND ML probability > 0.55
- **SELL**: Bollinger overbought (Percent_B > 0.9) OR ML probability < 0.45

#### 3. FYERS API Integration
- Historical data fetching via FYERS API
- Market order execution (CNC product type)
- Authentication flow implemented
- Symbol: NSE:SONATSOFTW-EQ

### Critical Implementation Details

#### Walk-Forward Methodology
- Each prediction uses ONLY data available up to that point
- Fresh `MLModel()` instance created for each prediction step
- No scaler state contamination between iterations
- Prevents data leakage from future information

#### Prediction Output
- Directional signals (UP/DOWN) with confidence scores
- NO fabricated price paths or returns
- Predictions based on learned patterns from historical features
- Output format: `date, predicted_direction, confidence`

#### Execution Logic
- Signals generated at day T execute at day T+1 open price
- Next-day open execution (realistic with market orders)
- 95% of capital allocated per trade
- Single position limit (no pyramiding)

### Project Structure
```
.
├── ml/
│   ├── features.py          # Feature engineering
│   ├── model.py             # ML model wrapper
│   ├── train.py             # Training pipeline
│   └── predict.py           # Prediction generator
├── fyers/
│   ├── auth.py              # FYERS authentication
│   ├── data.py              # Historical data fetch
│   └── orders.py            # Order execution
├── data/
│   └── sonata_software.csv  # Historical OHLCV data
├── run_pipeline.py          # Main execution script
├── predictions_jan_2026.csv # Competition predictions
└── README.md
```

### Installation
```bash
pip install pandas numpy scikit-learn fyers-apiv3 joblib
```

### Usage

#### Run Complete Pipeline
```bash
python run_pipeline.py
```

This executes:
1. ML model training on historical data
2. Walk-forward backtest with ML-enhanced signals
3. Jan 1-8, 2026 predictions generation
4. Results saved to CSV/JSON

#### FYERS API Setup
```bash
export FYERS_CLIENT_ID='your_client_id'
export FYERS_SECRET_KEY='your_secret_key'
export FYERS_REDIRECT_URI='https://www.google.com'
```

#### Generate Authentication URL
```python
from fyers.auth import FyersAuth
auth = FyersAuth()
print(auth.generate_auth_url())
```

### Competition Compliance

#### Required Deliverables
- ✅ Machine Learning model (Logistic Regression)
- ✅ FYERS API integration (auth, data, orders)
- ✅ Walk-forward backtest (no look-ahead bias)
- ✅ Jan 1-8, 2026 predictions (`predictions_jan_2026.csv`)
- ✅ Clean, modular code structure
- ✅ Documentation

#### Performance Metrics
- **Model**: Logistic Regression with 4 technical features
- **Backtest Period**: Nov 1 - Dec 31, 2025
- **Position Sizing**: 95% of capital
- **Execution**: Next-day open price
- **Risk Management**: Single position limit, mean reversion based

### Output Files
- `ml_model.pkl` - Trained ML model
- `ml_enhanced_trades.csv` - Trade log with ML probabilities
- `predictions_jan_2026.csv` - Next 5 days predictions
- `ml_backtest_metrics.json` - Performance summary

### Predictions Format
```csv
date,predicted_direction,confidence
2026-01-01,UP,0.5823
2026-01-02,DOWN,0.4651
2026-01-03,UP,0.6102
...
```

### Key Assumptions
- Market: NSE India
- Timeframe: Daily bars
- Execution: Next-day open (T+1 execution)
- No transaction costs in backtest
- FYERS API for live execution

### Competition Requirements Met
1. **ML Integration**: Logistic Regression enhances Bollinger signals
2. **FYERS API**: Complete implementation for data + orders
3. **Predictions**: 5-day directional forecast for Jan 2026
4. **Walk-Forward**: Fresh model instances, no future data leakage
5. **Code Quality**: Modular, documented, production-ready

### Security Notice
- Never commit FYERS credentials to repository
- Use environment variables for API keys
- `.gitignore` excludes sensitive files

### License
MIT License - IIT Kharagpur KSHITIJ 2026 Competition Submission
