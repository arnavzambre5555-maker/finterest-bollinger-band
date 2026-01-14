# ============================================================================
# FIXED VERSION - Copy this entire cell
# ============================================================================

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# STEP 1: LOAD DATA (FIXED DATE FORMAT)
df = pd.read_csv('Sonata_Software.csv')
df['date'] = pd.to_datetime(df['date'], dayfirst=True)  # ← FIXED THIS LINE
df.set_index('date', inplace=True)
df = df.sort_index()

print("="*80)
print("DATA LOADED SUCCESSFULLY")
print("="*80)
print(f"Total trading days: {len(df)}")
print(f"Period: {df.index[0].date()} to {df.index[-1].date()}")
print(f"\nFirst 5 rows:")
print(df.head())

# STEP 2: CALCULATE BOLLINGER BANDS
def calculate_bollinger_bands(df, window=20, num_std=2.0):
    df = df.copy()
    df['SMA'] = df['close'].rolling(window=window).mean()
    df['STD'] = df['close'].rolling(window=window).std()
    df['Upper_Band'] = df['SMA'] + (num_std * df['STD'])
    df['Lower_Band'] = df['SMA'] - (num_std * df['STD'])
    df['Percent_B'] = (df['close'] - df['Lower_Band']) / (df['Upper_Band'] - df['Lower_Band'])
    df['Bandwidth'] = (df['Upper_Band'] - df['Lower_Band']) / df['SMA']
    return df

df = calculate_bollinger_bands(df, window=20, num_std=2.0)

print("\n" + "="*80)
print("BOLLINGER BANDS CALCULATED")
print("="*80)
print("\nSample with indicators:")
print(df[['close', 'SMA', 'Upper_Band', 'Lower_Band', 'Percent_B']].tail(10))

# STEP 3: GENERATE SIGNALS
def generate_signals(df, oversold=0.1, overbought=0.9):
    df = df.copy()
    df['Signal'] = 0
    df.loc[df['Percent_B'] < oversold, 'Signal'] = 1
    df.loc[df['Percent_B'] > overbought, 'Signal'] = -1
    return df

df = generate_signals(df)

print("\n" + "="*80)
print("SIGNALS GENERATED")
print("="*80)
print(f"BUY signals: {len(df[df['Signal'] == 1])}")
print(f"SELL signals: {len(df[df['Signal'] == -1])}")

# STEP 4: BACKTEST
def backtest_strategy(df, initial_capital=100000, position_size_pct=0.95):
    df = df.copy()
    capital = initial_capital
    position = 0
    position_price = 0
    trades = []
    
    df['Position'] = 0
    df['Cash'] = initial_capital
    df['Holdings'] = 0.0
    df['Total'] = initial_capital
    df['Trade'] = ''
    
    print("\n" + "="*80)
    print("TRADE EXECUTION LOG")
    print("="*80 + "\n")
    
    for i in range(len(df)):
        current_price = df.iloc[i]['close']
        signal = df.iloc[i]['Signal']
        
        if signal == 1 and position == 0:
            shares_to_buy = int((capital * position_size_pct) / current_price)
            
            if shares_to_buy > 0:
                cost = shares_to_buy * current_price
                capital -= cost
                position = shares_to_buy
                position_price = current_price
                
                trade_msg = f'BUY {shares_to_buy} @ ₹{current_price:.2f}'
                df.at[df.index[i], 'Trade'] = trade_msg
                
                trades.append({
                    'Date': df.index[i],
                    'Type': 'BUY',
                    'Price': current_price,
                    'Shares': shares_to_buy,
                    'Value': cost,
                    'Percent_B': df.iloc[i]['Percent_B']
                })
                
                print(f"📈 {df.index[i].date()} | {trade_msg} | %B: {df.iloc[i]['Percent_B']:.3f}")
        
        elif signal == -1 and position > 0:
            revenue = position * current_price
            profit = (current_price - position_price) * position
            profit_pct = (profit / (position * position_price)) * 100
            
            capital += revenue
            
            trade_msg = f'SELL {position} @ ₹{current_price:.2f} | P&L: ₹{profit:.2f}'
            df.at[df.index[i], 'Trade'] = trade_msg
            
            trades.append({
                'Date': df.index[i],
                'Type': 'SELL',
                'Price': current_price,
                'Shares': position,
                'Value': revenue,
                'Profit': profit,
                'Profit_Pct': profit_pct,
                'Percent_B': df.iloc[i]['Percent_B']
            })
            
            print(f"📉 {df.index[i].date()} | {trade_msg} ({profit_pct:+.2f}%) | %B: {df.iloc[i]['Percent_B']:.3f}")
            
            position = 0
            position_price = 0
        
        df.at[df.index[i], 'Position'] = position
        df.at[df.index[i], 'Cash'] = capital
        df.at[df.index[i], 'Holdings'] = position * current_price
        df.at[df.index[i], 'Total'] = capital + (position * current_price)
    
    return df, trades

df, trades = backtest_strategy(df, initial_capital=100000, position_size_pct=0.95)

# STEP 5: PERFORMANCE METRICS
def calculate_metrics(df, trades, initial_capital=100000):
    final_value = df['Total'].iloc[-1]
    total_return = ((final_value - initial_capital) / initial_capital) * 100
    
    rolling_max = df['Total'].expanding().max()
    drawdown = (df['Total'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100
    
    returns = df['Total'].pct_change().dropna()
    if len(returns) > 0 and returns.std() != 0:
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
    else:
        sharpe_ratio = 0
    
    sell_trades = [t for t in trades if t['Type'] == 'SELL']
    
    if len(sell_trades) > 0:
        winning_trades = [t for t in sell_trades if t['Profit'] > 0]
        losing_trades = [t for t in sell_trades if t['Profit'] <= 0]
        
        win_rate = (len(winning_trades) / len(sell_trades)) * 100
        avg_win = np.mean([t['Profit'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['Profit'] for t in losing_trades]) if losing_trades else 0
        
        total_wins = sum([t['Profit'] for t in winning_trades]) if winning_trades else 0
        total_losses = sum([abs(t['Profit']) for t in losing_trades]) if losing_trades else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
    else:
        win_rate = avg_win = avg_loss = profit_factor = 0
    
    return {
        'Initial Capital (₹)': initial_capital,
        'Final Value (₹)': final_value,
        'Net Profit (₹)': final_value - initial_capital,
        'Total Return (%)': total_return,
        'Max Drawdown (%)': max_drawdown,
        'Sharpe Ratio': sharpe_ratio,
        'Total Trades': len(trades),
        'Buy Trades': len([t for t in trades if t['Type'] == 'BUY']),
        'Sell Trades': len(sell_trades),
        'Win Rate (%)': win_rate,
        'Winning Trades': len([t for t in sell_trades if t.get('Profit', 0) > 0]),
        'Losing Trades': len([t for t in sell_trades if t.get('Profit', 0) <= 0]),
        'Avg Win (₹)': avg_win,
        'Avg Loss (₹)': avg_loss,
        'Profit Factor': profit_factor,
    }

metrics = calculate_metrics(df, trades)

print("\n" + "="*80)
print("PERFORMANCE METRICS")
print("="*80)

for key, value in metrics.items():
    if isinstance(value, float):
        if 'Ratio' in key or 'Factor' in key:
            print(f"{key:.<45} {value:>15.2f}")
        elif '(%)' in key:
            print(f"{key:.<45} {value:>14.2f}%")
        elif '(₹)' in key:
            print(f"{key:.<45} ₹{value:>14,.2f}")
        else:
            print(f"{key:.<45} {value:>15.2f}")
    else:
        print(f"{key:.<45} {value:>15,}")

print("\n" + "="*80)
print("COMPETITION REQUIREMENTS CHECK")
print("="*80)
sharpe_pass = "✅ PASS" if metrics['Sharpe Ratio'] > 1.5 else "❌ FAIL"
return_pass = "✅ PASS" if metrics['Total Return (%)'] > 0 else "❌ FAIL"

print(f"Sharpe Ratio > 1.5: {metrics['Sharpe Ratio']:.2f} {sharpe_pass}")
print(f"Positive Returns: {metrics['Total Return (%)']:.2f}% {return_pass}")
print(f"Max Drawdown: {abs(metrics['Max Drawdown (%)']):.2f}% (lower is better)")

# STEP 6: SAVE RESULTS
df.to_csv('backtest_results.csv')
print("\n✅ Saved: backtest_results.csv")

if trades:
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv('trade_log.csv', index=False)
    print("✅ Saved: trade_log.csv")
    
    print("\n" + "="*80)
    print("TRADE LOG")
    print("="*80)
    print(trades_df.to_string(index=False))

import json
with open('performance_metrics.json', 'w') as f:
    json.dump({k: float(v) if isinstance(v, (int, float, np.number)) else v 
               for k, v in metrics.items()}, f, indent=4)
print("✅ Saved: performance_metrics.json")

print("\n" + "="*80)
print("🎉 STRATEGY BACKTESTING COMPLETE!")
print("="*80)

summary = f"""
📊 BOLLINGER BANDS STRATEGY RESULTS

Stock: Sonata Software (SONATSOFTW.NS)
Period: {df.index[0].date()} to {df.index[-1].date()}

💰 PERFORMANCE:
   Return:        {metrics['Total Return (%)']:.2f}%
   Sharpe Ratio:  {metrics['Sharpe Ratio']:.2f}
   Max Drawdown:  {abs(metrics['Max Drawdown (%)']):.2f}%
   Win Rate:      {metrics['Win Rate (%)']:.2f}%

Ready for IIT submission! 🚀
"""

print(summary)
