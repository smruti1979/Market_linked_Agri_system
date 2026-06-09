import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from statsmodels.tsa.holtwinters import ExponentialSmoothing

class MLPredictiveEngine:
    def __init__(self):
        self.crop_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.encoder = LabelEncoder()
        self.feature_names = ['N', 'P', 'K', 'ph', 'historical_rainfall_mm']

    def train_crop_recommender(self, df_fields):
        # Inject rule-based classification labels for synthetic PoC mapping
        conditions = [
            (df_fields['N'] > 80) & (df_fields['historical_rainfall_mm'] > 800),
            (df_fields['N'] <= 80) & (df_fields['historical_rainfall_mm'] > 600),
            (df_fields['K'] > 100) & (df_fields['historical_rainfall_mm'] <= 600),
        ]
        choices = ['Cotton', 'Soyabean', 'Onion']
        df_fields['optimal_crop'] = np.select(conditions, choices, default='Potato')
        
        X = df_fields[self.feature_names]
        y = df_fields['optimal_crop']
        
        y_encoded = self.encoder.fit_transform(y)
        self.crop_model.fit(X, y_encoded)

    def predict_top_crops(self, soil_profile):
        # FIX: Wrap vector array in a DataFrame with identical structural column keys to stop warnings
        features_df = pd.DataFrame([soil_profile], columns=self.feature_names)
        probs = self.crop_model.predict_proba(features_df)[0]
        top_indices = np.argsort(probs)[-2:] # Grab top two selections
        return self.encoder.inverse_transform(top_indices)

    def forecast_mandi_price(self, df_mandi, mandi, commodity, steps=90):
        node_data = df_mandi[(df_mandi['mandi_name'] == mandi) & (df_mandi['commodity'] == commodity)].copy()
        node_data['date'] = pd.to_datetime(node_data['date'])
        
        # FIX: Strip out text labels, leaving only the numerical metric for time-series math operations
        node_data = node_data[['date', 'modal_price_q']]
        node_data = node_data.sort_values('date').set_index('date').resample('D').mean().ffill()
        
        # Fast, robust time series smoothing
        model = ExponentialSmoothing(node_data['modal_price_q'], trend='add', seasonal=None)
        fit = model.fit()
        forecast = fit.forecast(steps)
        return max(500, forecast.iloc[-1])
