"""
Backtest Engine with Walk-Forward Testing
No look-ahead bias, realistic execution
"""

import pandas as pd
import numpy as np
from datetime import datetime

class BacktestEngine:
    """
    Walk-forward backtest engine with proper execution logic.
    Executes at open of t+1 based on signal at close of t.
    """
    
    def __init__(self, strategy, initial_capital=100000, position_size_pct=0.95):
        """
        Initialize backtest engine.
        
        Parameters:
        -----------
        strategy : Strategy object
            Trading strategy with calculate_indicators() and generate_signals()
        initial_capital : float
            Starting capital in INR (default: 100,000)
        position_size_pct : float
            Percentage of capital to use per trade (default: 0.95)
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct
        
    def run(self, df):
        """
        Execute backtest with no look-ahead bias.
        
        Execution flow:
        1. Calculate indicators on day t using data up to day t
        2. Generate signal at end of day t
        3. Execute trade at open of day t+1
        
        Returns:
        --------
        df_result : DataFrame with portfolio values
        trades : List of trade dictionaries
        """
        df = df.copy()
        
        # Calculate indicators and signals
        df = self.strategy.calculate_indicators(df)
        df = self.strategy.generate_signals(df)
        
        # Initialize portfolio tracking
        capital = self.initial_capital
        position = 0  # shares held
        position_price = 0  # entry price
        trades = []
        
        # Add portfolio tracking columns
        df['Position'] = 0
        df['Cash'] = self.initial_capital
        df['Holdings'] = 0.0
        df['Total'] = self.initial_capital
        
        # Walk forward through history
        for i in range(len(df) - 1):  # Stop at -1 to avoid index error
            signal = df.iloc[i]['Signal']
            
            # BUY LOGIC
            if signal == 1 and position == 0:
                # Execute at OPEN of next day
                execution_price = df.iloc[i+1]['open']
                shares = int((capital * self.position_size_pct) / execution_price)
                
                if shares > 0:
                    cost = shares * execution_price
                    capital -= cost
                    position = shares
                    position_price = execution_price
                    
                    trades.append({
                        'Signal_Date': df.index[i],
                        'Execution_Date': df.index[i+1],
                        'Type': 'BUY',
                        'Price': execution_price,
                        'Shares': shares,
                        'Value': cost,
                        'Percent_B': df.iloc[i]['Percent_B']
                    })
            
            # SELL LOGIC
            elif signal == -1 and position > 0:
                # Execute at OPEN of next day
                execution_price = df.iloc[i+1]['open']
                revenue = position * execution_price
                profit = (execution_price - position_price) * position
                profit_pct = (profit / (position * position_price)) * 100
                
                capital += revenue
                
                trades.append({
                    'Signal_Date': df.index[i],
                    'Execution_Date': df.index[i+1],
                    'Type': 'SELL',
                    'Price': execution_price,
                    'Shares': position,
                    'Value': revenue,
                    'Profit': profit,
                    'Profit_Pct': profit_pct,
                    'Percent_B': df.iloc[i]['Percent_B']
                })
                
                position = 0
                position_price = 0
            
            # Update portfolio values at CLOSE of day i+1
            current_price = df.iloc[i+1]['close']
            df.at[df.index[i+1], 'Position'] = position
            df.at[df.index[i+1], 'Cash'] = capital
            df.at[df.index[i+1], 'Holdings'] = position * current_price
            df.at[df.index[i+1], 'Total'] = capital + (position * current_price)
        
        return df, trades
    
    def calculate_metrics(self, df, trades):
        """
        Calculate performance metrics without look-ahead bias.
        
        Metrics:
        - Total Return
        - Maximum Drawdown
        - Sharpe Ratio (annualized)
        - Win Rate
        - Average Win/Loss
        """
        initial_capital = self.initial_capital
        final_value = df['Total'].iloc[-1]
        total_return = ((final_value - initial_capital) / initial_capital) * 100
        
        # Maximum Drawdown
        rolling_max = df['Total'].expanding().max()
        drawdown = (df['Total'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # Sharpe Ratio (annualized)
        returns = df['Total'].pct_change().dropna()
        if len(returns) > 1 and returns.std() != 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # Trade statistics
        sell_trades = [t for t in trades if t['Type'] == 'SELL']
        
        if len(sell_trades) > 0:
            winning_trades = [t for t in sell_trades if t['Profit'] > 0]
            win_rate = (len(winning_trades) / len(sell_trades)) * 100
            avg_win = np.mean([t['Profit'] for t in winning_trades]) if winning_trades else 0
            
            losing_trades = [t for t in sell_trades if t['Profit'] <= 0]
            avg_loss = np.mean([abs(t['Profit']) for t in losing_trades]) if losing_trades else 0
        else:
            win_rate = avg_win = avg_loss = 0
        
        return {
            'Initial_Capital': initial_capital,
            'Final_Value': final_value,
            'Net_Profit': final_value - initial_capital,
            'Total_Return_Pct': total_return,
            'Max_Drawdown_Pct': max_drawdown,
            'Sharpe_Ratio': sharpe_ratio,
            'Total_Trades': len(trades),
            'Win_Rate_Pct': win_rate,
            'Avg_Win': avg_win,
            'Avg_Loss': avg_loss
        }
