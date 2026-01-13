import pandas as pd
import json
from datetime import datetime
from fyers_data import get_fyers_data
from strategy import calculate_bollinger_bands, generate_ml_signals, backtest_strategy, calculate_performance_metrics
from ml_model import MLTradingModel

def main():
    print("=" * 60)
    print("ML-DRIVEN BOLLINGER BANDS TRADING SYSTEM")
    print("=" * 60)
    
    # Parameters
    symbol = "NSE:SBIN-EQ"
    train_start = "2025-11-01"
    train_end = "2025-12-31"
    
    # Step 1: Load training data
    print(f"\n[1/6] Loading training data from {train_start} to {train_end}...")
    train_df = get_fyers_data(symbol, train_start, train_end)
    
    if train_df is None or len(train_df) == 0:
        print("ERROR: Failed to load training data")
        return
    
    print(f"Loaded {len(train_df)} training records")
    
    # Step 2: Calculate Bollinger Bands features
    print("\n[2/6] Calculating Bollinger Bands indicators...")
    train_df = calculate_bollinger_bands(train_df, window=20, num_std=2)
    print(f"Features calculated: {['Percent_B', 'Bandwidth', 'SMA', 'STD']}")
    
    # Step 3: Train ML model
    print("\n[3/6] Training ML model...")
    ml_model = MLTradingModel()
    
    try:
        ml_model.train(train_df)
        ml_model.save_model('trained_model.pkl')
        print("✓ Model trained and saved as 'trained_model.pkl'")
        print(f"✓ Training frozen on: {train_end}")
    except Exception as e:
        print(f"ERROR: Failed to train model - {str(e)}")
        return
    
    # Step 4: Backtest on training period
    print("\n[4/6] Running backtest on training period...")
    train_df = generate_ml_signals(train_df, ml_model, buy_threshold=0.55, sell_threshold=0.45)
    backtest_df, trades_df, final_capital = backtest_strategy(train_df, initial_capital=100000, position_size=0.95)
    
    # Calculate metrics
    metrics = calculate_performance_metrics(backtest_df, trades_df, final_capital, 100000)
    
    print("\n" + "=" * 60)
    print("BACKTEST RESULTS (Training Period)")
    print("=" * 60)
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Save backtest results
    with open('results_summary.json', 'w') as f:
        json.dump(metrics, f, indent=4)
    print("\n✓ Backtest results saved to 'results_summary.json'")
    
    # Save trades log
    if len(trades_df) > 0:
        trades_df.to_csv('trades_log.csv', index=False)
        print("✓ Trades log saved to 'trades_log.csv'")
    else:
        # Create empty trades log
        pd.DataFrame(columns=['Date', 'Action', 'Price', 'Shares', 'Capital']).to_csv('trades_log.csv', index=False)
        print("✓ Empty trades log saved to 'trades_log.csv'")
    
    # Step 5: Generate forward predictions (MANDATORY - NO FUTURE DATA)
    print("\n[5/6] Generating 5-day forward prediction (Jan 1-8, 2026)...")
    print("Using frozen model state from Dec 31, 2025...")
    
    try:
        # Use last available state from Dec 31, 2025 (NO FUTURE DATA)
        last_state = train_df.iloc[-1:]
        
        # Generate prediction using frozen model
        predictions = ml_model.predict_proba(last_state)
        
        if len(predictions) == 0:
            raise ValueError("Failed to generate prediction from last state")
        
        # Extract single prediction
        pred_row = predictions.iloc[0]
        
        # Create forward prediction (5-day forecast)
        forward_predictions = {
            "symbol": symbol,
            "prediction_period": "2026-01-01 to 2026-01-08",
            "model_frozen_on": train_end,
            "forecast_horizon": "5 trading days",
            "last_training_date": str(train_df.index[-1].date()) if hasattr(train_df.index[-1], 'date') else str(train_df.index[-1]),
            "probability_up": round(float(pred_row['prob_up']), 4),
            "probability_down": round(float(pred_row['prob_down']), 4),
            "predicted_direction": pred_row['predicted_direction'],
            "note": "Prediction generated from frozen model state as of Dec 31, 2025. No future data used."
        }
        
        print(f"✓ Forward prediction generated")
        print(f"  Probability UP: {forward_predictions['probability_up']}")
        print(f"  Probability DOWN: {forward_predictions['probability_down']}")
        print(f"  Direction: {forward_predictions['predicted_direction']}")
        
    except Exception as e:
        print(f"ERROR: Failed to generate forward prediction - {str(e)}")
        forward_predictions = {
            "symbol": symbol,
            "prediction_period": "2026-01-01 to 2026-01-08",
            "model_frozen_on": train_end,
            "error": str(e)
        }
    
    # Save forward predictions (MANDATORY OUTPUT)
    with open('predictions_jan_2026.json', 'w') as f:
        json.dump(forward_predictions, f, indent=4)
    
    print("✓ Forward predictions saved to 'predictions_jan_2026.json'")
    
    # Step 6: Compliance check
    print("\n[6/6] Compliance check...")
    required_files = [
        'trained_model.pkl',
        'predictions_jan_2026.json',
        'results_summary.json',
        'trades_log.csv'
    ]
    
    import os
    all_present = True
    for file in required_files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_present = False
    
    print("\n" + "=" * 60)
    if all_present:
        print("SUCCESS: All compliance outputs generated")
        print("=" * 60)
        print("\nSUMMARY:")
        print(f"  • Model trained on: {train_start} to {train_end}")
        print(f"  • Model frozen on: {train_end}")
        print(f"  • Backtest trades: {metrics.get('Number of Trades', 0)}")
        print(f"  • Total return: {metrics.get('Total Return (%)', 0)}%")
        print(f"  • Sharpe ratio: {metrics.get('Sharpe Ratio', 0)}")
        print(f"  • Forward forecast: {forward_predictions.get('predicted_direction', 'N/A')}")
        print(f"  • NO FUTURE DATA USED IN PREDICTION")
    else:
        print("WARNING: Some required files missing")
    print("=" * 60)

if __name__ == "__main__":
    main()
