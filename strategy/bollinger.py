import pandas as pd
import numpy as np

def calculate_bollinger_bands(df, window=20, num_std=2):
    """Calculate Bollinger Bands indicators"""
    df = df.copy()
    
    df['SMA'] = df['Close'].rolling(window=window).mean()
    df['STD'] = df['Close'].rolling(window=window).std()
    
    df['Upper_Band'] = df['SMA'] + (df['STD'] * num_std)
    df['Lower_Band'] = df['SMA'] - (df['STD'] * num_std)
    
    df['Percent_B'] = (df['Close'] - df['Lower_Band']) / (df['Upper_Band'] - df['Lower_Band'])
    df['Bandwidth'] = (df['Upper_Band'] - df['Lower_Band']) / df['SMA']
    
    return df

def generate_ml_signals(df, ml_model, buy_threshold=0.55, sell_threshold=0.45):
    """Generate trading signals based on ML model predictions"""
    df = df.copy()
    
    # Get ML predictions
    predictions = ml_model.predict_proba(df)
    
    # Merge predictions with dataframe
    df = df.join(predictions[['prob_up', 'prob_down', 'predicted_direction']], how='left')
    
    # Initialize signal column
    df['Signal'] = 'HOLD'
    
    # Generate signals based on probability thresholds
    df.loc[df['prob_up'] > buy_threshold, 'Signal'] = 'BUY'
    df.loc[df['prob_up'] < sell_threshold, 'Signal'] = 'SELL'
    
    return df

def backtest_strategy(df, initial_capital=100000, position_size=0.95):
    """Backtest the ML-driven trading strategy"""
    df = df.copy()
    
    capital = initial_capital
    position = 0
    entry_price = 0
    
    trades = []
    capital_history = []
    
    for idx, row in df.iterrows():
        if pd.isna(row['Signal']):
            capital_history.append(capital)
            continue
        
        signal = row['Signal']
        current_price = row['Close']
        
        if signal == 'BUY' and position == 0:
            shares_to_buy = int((capital * position_size) / current_price)
            if shares_to_buy > 0:
                position = shares_to_buy
                entry_price = current_price
                capital -= shares_to_buy * current_price
                
                trades.append({
                    'Date': idx,
                    'Action': 'BUY',
                    'Price': current_price,
                    'Shares': shares_to_buy,
                    'Capital': capital,
                    'prob_up': row.get('prob_up', np.nan)
                })
        
        elif signal == 'SELL' and position > 0:
            capital += position * current_price
            
            trades.append({
                'Date': idx,
                'Action': 'SELL',
                'Price': current_price,
                'Shares': position,
                'Capital': capital,
                'Return': ((current_price - entry_price) / entry_price) * 100,
                'prob_up': row.get('prob_up', np.nan)
            })
            
            position = 0
            entry_price = 0
        
        portfolio_value = capital + (position * current_price)
        capital_history.append(portfolio_value)
    
    # Close any open position at the end
    if position > 0:
        final_price = df.iloc[-1]['Close']
        capital += position * final_price
        
        trades.append({
            'Date': df.index[-1],
            'Action': 'SELL',
            'Price': final_price,
            'Shares': position,
            'Capital': capital,
            'Return': ((final_price - entry_price) / entry_price) * 100,
            'prob_up': df.iloc[-1].get('prob_up', np.nan)
        })
    
    df['Portfolio_Value'] = capital_history
    
    return df, pd.DataFrame(trades), capital

def calculate_performance_metrics(df, trades_df, final_capital, initial_capital):
    """Calculate performance metrics"""
    total_return = ((final_capital - initial_capital) / initial_capital) * 100
    
    if 'Portfolio_Value' in df.columns:
        returns = df['Portfolio_Value'].pct_change().dropna()
        if len(returns) > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
            max_drawdown = ((df['Portfolio_Value'].cummax() - df['Portfolio_Value']) / df['Portfolio_Value'].cummax()).max() * 100
        else:
            sharpe_ratio = 0
            max_drawdown = 0
    else:
        sharpe_ratio = 0
        max_drawdown = 0
    
    num_trades = len(trades_df)
    
    if num_trades > 0 and 'Return' in trades_df.columns:
        winning_trades = trades_df[trades_df['Return'] > 0]
        win_rate = (len(winning_trades) / len(trades_df[trades_df['Action'] == 'SELL'])) * 100 if len(trades_df[trades_df['Action'] == 'SELL']) > 0 else 0
    else:
        win_rate = 0
    
    metrics = {
        'Total Return (%)': round(total_return, 2),
        'Sharpe Ratio': round(sharpe_ratio, 2),
        'Max Drawdown (%)': round(max_drawdown, 2),
        'Number of Trades': num_trades,
        'Win Rate (%)': round(win_rate, 2),
        'Final Capital': round(final_capital, 2),
        'Initial Capital': initial_capital
    }
    
    return metrics
