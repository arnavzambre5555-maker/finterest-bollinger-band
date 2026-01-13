import pandas as pd
from ml.features import FeatureEngineer
from ml.model import MLModel

def train_ml_model(df):
    fe = FeatureEngineer()
    df_features, feature_cols = fe.create_ml_features(df)
    
    df_features = df_features[df_features['Target'].notna()]
    
    X = df_features[feature_cols]
    y = df_features['Target']
    
    X = X[:-1]
    y = y[:-1]
    
    model = MLModel()
    model.train(X, y)
    
    return model, fe
