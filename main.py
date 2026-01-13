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
    predict_start = "2026-01-01"
    predict_end = "2026-01-08"
    
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
    
    # Step 5: Generate forward predictions (MANDATORY)
    print("\n[5/6] Generating forward predictions for Jan 1-8, 2026...")
    predict_df = get_fyers_data(symbol, predict_start, predict_end)
    
    if predict_df is None or len(predict_df) == 0:
        print("WARNING: No data available for prediction period")
        print("Creating predictions file with note...")
        
        # Create predictions file with note
        forward_predictions = {
            "symbol": symbol,
            "prediction_period": f"{predict_start} to {predict_end}",
            "model_frozen_on": train_end,
            "predictions": [],
            "note": "Market data not yet available for this future period. Model is frozen and ready for forward testing."
        }
    else:
        print(f"Loaded {len(predict_df)} records for prediction")
        
        # Calculate features for prediction
        predict_df = calculate_bollinger_bands(predict_df, window=20, num_std=2)
        
        # Generate predictions using frozen model
        try:
            predictions = ml_model.predict_proba(predict_df)
            
            # Prepare forward predictions output
            forward_predictions = {
                "symbol": symbol,
                "prediction_period": f"{predict_start} to {predict_end}",
                "model_frozen_on": train_end,
                "predictions": []
            }
            
            for date, row in predictions.iterrows():
                forward_predictions["predictions"].append({
                    "date": str(date.date()) if hasattr(date, 'date') else str(date),
                    "probability_up": round(float(row['prob_up']), 4),
                    "probability_down": round(float(row['prob_down']), 4),
                    "predicted_direction": row['predicted_direction']
                })
            
            print(f"✓ Generated {len(predictions)} forward predictions")
            
        except Exception as e:
            print(f"WARNING: Failed to generate predictions - {str(e)}")
            forward_predictions = {
                "symbol": symbol,
                "prediction_period": f"{predict_start} to {predict_end}",
                "model_frozen_on": train_end,
                "predictions": [],
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
        print(f"  • Forward predictions: {len(forward_predictions.get('predictions', []))}")
    else:
        print("WARNING: Some required files missing")
    print("=" * 60)

if __name__ == "__main__":
    main()
