# ===== ml_model.py =====
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pickle

class MLModel:
    def __init__(self):
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, df):
        df = df.copy()
        df = df.dropna()
        
        # Calculate 5-day forward return
        df['future_return'] = df['close'].shift(-5) / df['close'] - 1
        
        # Create target: 1 if forward return > 0, else 0
        df['target'] = (df['future_return'] > 0).astype(int)
        
        # Remove last 5 rows (no forward data)
        df = df[:-5]
        
        # Features: Percent_B, Bandwidth, SMA, STD
        features = ['Percent_B', 'Bandwidth', 'SMA', 'STD']
        X = df[features].values
        y = df['target'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        return self
    
    def predict_proba(self, df):
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        df = df.copy()
        features = ['Percent_B', 'Bandwidth', 'SMA', 'STD']
        X = df[features].values
        X_scaled = self.scaler.transform(X)
        
        # Returns [prob_down, prob_up]
        proba = self.model.predict_proba(X_scaled)
        return proba[:, 1]  # probability of up movement
    
    def save(self, filepath='trained_model.pkl'):
        with open(filepath, 'wb') as f:
            pickle.dump({'model': self.model, 'scaler': self.scaler}, f)
    
    def load(self, filepath='trained_model.pkl'):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = True
