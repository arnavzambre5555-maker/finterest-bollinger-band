"""
Main execution file for Bollinger Bands strategy
IIT Kharagpur AQUA Competition 2026
"""

import sys
import pandas as pd
import json

sys.path.append('strategy')
sys.path.append('backtest')

from bollinger import BollingerBandsStrategy
from backtest_engine import BacktestEngine

def main(data_path='data/sonata_software.csv'):
    """
    Execute backtest and display results.
    
    Parameters:
    -----------
    data_path : str
        Path to CSV file with OHLCV data
    """
    print("="*70)
    print("BOLLINGER BANDS TRADING STRATEGY")
    print("IIT Kharagpur AQUA Competition 2026")
    print("="*70)
    
    # Load data
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df.set_index('date', inplace=True)
    df = df.sort_index()
    
    print(f"\nData Period: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Trading Days: {len(df)}")
    
    # Initialize strategy and backtest engine
    strategy = BollingerBandsStrategy(
        window=20, 
        num_std=2.0, 
        oversold=0.1, 
        overbought=0.9
    )
    
    engine = BacktestEngine(
        strategy, 
        initial_capital=100000, 
        position_size_pct=0.95
    )
    
    # Run backtest
    print("\nRunning backtest...")
    df_result, trades = engine.run(df)
    metrics = engine.calculate_metrics(df_result, trades)
    
    # Display results
    print("\n" + "="*70)
    print("PERFORMANCE METRICS")
    print("="*70)
    print(f"  Initial Capital:    Rs. {metrics['Initial_Capital']:>12,.2f}")
    print(f"  Final Value:        Rs. {metrics['Final_Value']:>12,.2f}")
    print(f"  Net Profit:         Rs. {metrics['Net_Profit']:>12,.2f}")
    print(f"  Total Return:            {metrics['Total_Return_Pct']:>11.2f}%")
    print(f"  Max Drawdown:            {abs(metrics['Max_Drawdown_Pct']):>11.2f}%")
    print(f"  Sharpe Ratio:            {metrics['Sharpe_Ratio']:>15.2f}")
    print(f"  Win Rate:                {metrics['Win_Rate_Pct']:>11.2f}%")
    print(f"  Total Trades:            {metrics['Total_Trades']:>15}")
    
    # Competition requirements check
    print("\n" + "="*70)
    print("COMPETITION REQUIREMENTS")
    print("="*70)
    
    sharpe_pass = "PASS" if metrics['Sharpe_Ratio'] > 1.5 else "FAIL"
    return_pass = "PASS" if metrics['Total_Return_Pct'] > 0 else "FAIL"
    
    print(f"  Sharpe Ratio > 1.5:      {sharpe_pass}")
    print(f"  Positive Returns:        {return_pass}")
    
    # Save results
    if trades:
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv('backtest_trades.csv', index=False)
        print("\n✓ Saved: backtest_trades.csv")
    
    with open('backtest_metrics.json', 'w') as f:
        # Convert numpy types to Python types for JSON serialization
        metrics_json = {k: float(v) if isinstance(v, (float, int)) else v 
                       for k, v in metrics.items()}
        json.dump(metrics_json, f, indent=2)
    
    print("✓ Saved: backtest_metrics.json")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
