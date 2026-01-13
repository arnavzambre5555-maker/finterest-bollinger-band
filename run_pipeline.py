import sys
import pandas as pd
import json
from datetime import datetime

sys.path.append('.')

from strategy.bollinger import BollingerBandsStrategy
from backtest.backtest_engine import BacktestEngine
from ml.train import train_ml_model
from ml.predict import generate_predictions
from ml.features import FeatureEngineer
from ml.model import MLModel
from fyers.auth import FyersAuth
from fyers.data import FyersData
from fyers.orders import FyersOrders

def main():
    print("="*80)
    print("IIT KHARAGPUR KSHITIJ 2026 - AQUA COMPETITION")
    print("ML-ENHANCED BOLLINGER BANDS STRATEGY")
    print("="*80)
    
    df = pd.read_csv('data/sonata_software.csv')
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df.set_index('date', inplace=True)
    df = df.sort_index()
    
    print(f"\nData loaded: {len(df)} days")
    print(f"Period: {df.index[0].date()} to {df.index[-1].date()}")
    
    print("\n" + "="*80)
    print("STEP 1: TRAINING ML MODEL")
    print("="*80)
    
    ml_model, feature_engineer = train_ml_model(df)
    ml_model.save('ml_model.pkl')
    print("ML model trained and saved")
    
    print("\n" + "="*80)
    print("STEP 2: RUNNING ML-ENHANCED BACKTEST")
    print("="*80)
    
    fe = FeatureEngineer()
    df_features, feature_cols = fe.create_ml_features(df)
    
    # FIXED: Walk-forward with fresh model instances
    ml_proba = []
    for i in range(len(df_features)):
        if i < 20:
            ml_proba.append(0.5)
        else:
            X_train = df_features[feature_cols].iloc[:i]
            y_train = df_features['Target'].iloc[:i]
            
            # FIXED: Create fresh model instance each step
            temp_model = MLModel()
            temp_model.train(X_train, y_train)
            
            X_test = df_features[feature_cols].iloc[i:i+1]
            prob = temp_model.predict_proba(X_test)[0]
            ml_proba.append(prob)
    
    df_features['ML_Proba'] = ml_proba
    
    df_features['BB_Buy_Signal'] = (df_features['Percent_B'] < 0.1).astype(int)
    df_features['BB_Sell_Signal'] = (df_features['Percent_B'] > 0.9).astype(int)
    
    df_features['Final_Buy_Signal'] = (
        (df_features['BB_Buy_Signal'] == 1) & 
        (df_features['ML_Proba'] > 0.55)
    ).astype(int)
    
    df_features['Final_Sell_Signal'] = (
        (df_features['BB_Sell_Signal'] == 1) | 
        (df_features['ML_Proba'] < 0.45)
    ).astype(int)
    
    capital = 100000
    position = 0
    position_price = 0
    trades = []
    
    # FIXED: Next-day open execution
    for i in range(len(df_features) - 1):
        row = df_features.iloc[i]
        
        if row['Final_Buy_Signal'] == 1 and position == 0:
            next_open = df_features['open'].iloc[i+1]
            shares = int((capital * 0.95) / next_open)
            if shares > 0:
                cost = shares * next_open
                capital -= cost
                position = shares
                position_price = next_open
                
                trades.append({
                    'Date': df_features.index[i+1],
                    'Type': 'BUY',
                    'Price': next_open,
                    'Shares': shares,
                    'ML_Proba': row['ML_Proba'],
                    'Percent_B': row['Percent_B']
                })
                print(f"BUY  | {df_features.index[i+1].date()} | {shares} shares @ Rs.{next_open:.2f} | ML_Proba: {row['ML_Proba']:.3f}")
        
        elif row['Final_Sell_Signal'] == 1 and position > 0:
            next_open = df_features['open'].iloc[i+1]
            revenue = position * next_open
            profit = (next_open - position_price) * position
            profit_pct = (profit / (position * position_price)) * 100
            
            capital += revenue
            
            trades.append({
                'Date': df_features.index[i+1],
                'Type': 'SELL',
                'Price': next_open,
                'Shares': position,
                'Profit': profit,
                'Profit_Pct': profit_pct,
                'ML_Proba': row['ML_Proba'],
                'Percent_B': row['Percent_B']
            })
            
            print(f"SELL | {df_features.index[i+1].date()} | {position} shares @ Rs.{next_open:.2f} | P&L: Rs.{profit:.2f} ({profit_pct:+.2f}%)")
            
            position = 0
            position_price = 0
    
    final_value = capital + (position * df_features['close'].iloc[-1])
    total_return = ((final_value - 100000) / 100000) * 100
    
    print(f"\nFinal Portfolio Value: Rs.{final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total Trades: {len(trades)}")
    
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv('ml_enhanced_trades.csv', index=False)
    
    print("\n" + "="*80)
    print("STEP 3: GENERATING JAN 1-8, 2026 PREDICTIONS")
    print("="*80)
    
    predictions = generate_predictions(df, ml_model, feature_engineer, n_days=5)
    predictions.to_csv('predictions_jan_2026.csv', index=False)
    
    print("\nPredictions for next 5 trading days:")
    print(predictions.to_string(index=False))
    
    metrics = {
        'Final_Value': final_value,
        'Total_Return_Pct': total_return,
        'Total_Trades': len(trades),
        'ML_Model': 'Logistic Regression',
        'Features': feature_cols,
        'Execution': 'Next-day open price'
    }
    
    with open('ml_backtest_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("\n" + "="*80)
    print("PIPELINE COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    print("  - ml_model.pkl")
    print("  - ml_enhanced_trades.csv")
    print("  - predictions_jan_2026.csv")
    print("  - ml_backtest_metrics.json")
    
    print("\n" + "="*80)
    print("FYERS API INTEGRATION")
    print("="*80)
    print("\nTo execute live trades:")
    print("1. Set environment variables:")
    print("   export FYERS_CLIENT_ID='your_client_id'")
    print("   export FYERS_SECRET_KEY='your_secret_key'")
    print("2. Run authentication:")
    print("   python -c \"from fyers.auth import FyersAuth; auth = FyersAuth(); print(auth.generate_auth_url())\"")
    print("3. Use generated token for live trading")

if __name__ == "__main__":
    main()
