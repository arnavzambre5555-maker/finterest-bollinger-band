"""
Bollinger Bands Trading Strategy
Mean reversion strategy for NSE equities
"""

import pandas as pd
import numpy as np

class BollingerBandsStrategy:
    """
    Bollinger Bands mean reversion strategy.
    Generates signals on day t for execution at open of t+1.
    """
    
    def __init__(self, window=20, num_std=2.0, oversold=0.1, overbought=0.9):
        """
        Initialize strategy parameters.
        
        Parameters:
        -----------
        window : int
            Rolling window for SMA calculation (default: 20 days)
        num_std : float
            Number of standard deviations for bands (default: 2.0)
        oversold : float
            Percent_B threshold for buy signal (default: 0.1)
        overbought : float
            Percent_B threshold for sell signal (default: 0.9)
        """
        self.window = window
        self.num_std = num_std
        self.oversold = oversold
        self.overbought = overbought
        
    def calculate_indicators(self, df):
        """
        Calculate Bollinger Bands and derived metrics.
        
        Returns DataFrame with added columns:
        - SMA: Simple Moving Average
        - STD: Standard Deviation
        - Upper_Band, Lower_Band: Bollinger Bands
        - Percent_B: Position within bands (0 to 1)
        - Bandwidth: Band width normalized by SMA
        """
        df = df.copy()
        
        # Calculate Bollinger Bands
        df['SMA'] = df['close'].rolling(window=self.window).mean()
        df['STD'] = df['close'].rolling(window=self.window).std()
        df['Upper_Band'] = df['SMA'] + (self.num_std * df['STD'])
        df['Lower_Band'] = df['SMA'] - (self.num_std * df['STD'])
        
        # Percent B: where price is within the bands
        df['Percent_B'] = (df['close'] - df['Lower_Band']) / (
            df['Upper_Band'] - df['Lower_Band']
        )
        
        # Bandwidth: volatility measure
        df['Bandwidth'] = (df['Upper_Band'] - df['Lower_Band']) / df['SMA']
        
        return df
    
    def generate_signals(self, df):
        """
        Generate trading signals based on Percent_B.
        
        Signal logic:
        - Signal = 1 (BUY): Percent_B < oversold threshold
        - Signal = -1 (SELL): Percent_B > overbought threshold
        - Signal = 0 (HOLD): Otherwise
        
        Signal generated on day t for execution at open of t+1.
        """
        df = df.copy()
        df['Signal'] = 0
        
        # BUY when oversold
        df.loc[df['Percent_B'] < self.oversold, 'Signal'] = 1
        
        # SELL when overbought
        df.loc[df['Percent_B'] > self.overbought, 'Signal'] = -1
        
        return df
