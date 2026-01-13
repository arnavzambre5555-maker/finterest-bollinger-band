import pandas as pd
import numpy as np

def generate_predictions(df, model, fe, n_days=5):
    """
    Generate directional predictions for next N trading days.
    Does NOT fabricate price paths - outputs direction and confidence only.
    """
    df_features, feature_cols = fe.create_ml_features(df)
    
    # Get latest features for prediction
    latest_features = df_features[feature_cols].iloc[-1:].copy()
    
    predictions = []
    pred_dates = pd.date_range(start='2026-01-01', periods=n_days, freq='B')
    
    for date in pred_dates:
        prob = model.predict_proba(latest_features)[0]
        direction = 'UP' if prob > 0.5 else 'DOWN'
        
        predictions.append({
            'date': date.strftime('%Y-%m-%d'),
            'predicted_direction': direction,
            'confidence': round(prob, 4)
        })
    
    pred_df = pd.DataFrame(predictions)
    return pred_df
