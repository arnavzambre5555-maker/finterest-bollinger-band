import pandas as pd
import numpy as np

class FeatureEngineer:
    def __init__(self, window=20, num_std=2.0):
        self.window = window
        self.num_std = num_std
    
    def calculate_bollinger_bands(self, df):
        df = df.copy()
        df['SMA'] = df['close'].rolling(window=self.window).mean()
        df['STD'] = df['close'].rolling(window=self.window).std()
        df['Upper_Band'] = df['SMA'] + (self.num_std * df['STD'])
        df['Lower_Band'] = df['SMA'] - (self.num_std * df['STD'])
        df['Percent_B'] = (df['close'] - df['Lower_Band']) / (df['Upper_Band'] - df['Lower_Band'])
        df['Bandwidth'] = (df['Upper_Band'] - df['Lower_Band']) / df['SMA']
        return df
    
    def create_ml_features(self, df):
        df = df.copy()
        df = self.calculate_bollinger_bands(df)
        
        df['Distance_from_SMA'] = (df['close'] - df['SMA']) / df['SMA']
        df['Return_1d'] = df['close'].pct_change(1)
        
        df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)
        
        feature_cols = ['Percent_B', 'Bandwidth', 'Distance_from_SMA', 'Return_1d']
        
        # FIXED: Only drop NaN in features, not Target
        df_clean = df.dropna(subset=feature_cols)
        
        return df_clean, feature_cols
