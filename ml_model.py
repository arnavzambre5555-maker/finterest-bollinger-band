import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import warnings
warnings.filterwarnings('ignore')

class MLTradingModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.scaler = StandardScaler()
        self.feature_columns = ['Percent_B', 'Bandwidth', 'SMA', 'STD']
        self.is_trained = False
        
    def prepare_features(self, df):
        """Extract features from dataframe"""
        features = df[self.feature_columns].copy()
        features = features.dropna()
        return features
    
    def create_target(self, df, forward_days=5):
        """Create target variable: 1 if 5-day forward return > 0, else 0"""
        df = df.copy()
        df['future_close'] = df['Close'].shift(-forward_days)
        df['forward_return'] = (df['future_close'] - df['Close']) / df['Close']
        df['target'] = (df['forward_return'] > 0).astype(int)
        return df
    
    def train(self, df):
        """Train the model on historical data"""
        df_with_target = self.create_target(df, forward_days=5)
        
        # Remove rows with NaN in features or target
        df_clean = df_with_target.dropna(subset=self.feature_columns + ['target'])
        
        if len(df_clean) < 20:
            raise ValueError("Insufficient training data after cleaning")
        
        X = df_clean[self.feature_columns].values
        y = df_clean['target'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        print(f"Model trained on {len(X)} samples")
        print(f"Target distribution: {np.bincount(y)}")
        
        return self
    
    def predict_proba(self, df):
        """Predict probability of upward movement - returns DataFrame"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        df = df.copy()
        
        # Guard against NaNs at prediction time
        df_clean = df.dropna(subset=self.feature_columns)
        
        if len(df_clean) == 0:
            return pd.DataFrame()
        
        X = df_clean[self.feature_columns].values
        X_scaled = self.scaler.transform(X)
        
        proba = self.model.predict_proba(X_scaled)
        
        # Return DataFrame with proper columns expected by strategy
        result = pd.DataFrame({
            'prob_down': proba[:, 0],
            'prob_up': proba[:, 1],
            'predicted_direction': np.where(proba[:, 1] > 0.5, 'UP', 'DOWN')
        }, index=df_clean.index)
        
        return result
    
    def save_model(self, filepath='trained_model.pkl'):
        """Save trained model and scaler"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='trained_model.pkl'):
        """Load trained model and scaler"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = True
        
        print(f"Model loaded from {filepath}")
        return self
