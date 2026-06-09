import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_farmer_field_data(num_records=100):
    np.random.seed(42)
    data = {
        'farmer_id': [f"FARM_{i:03d}" for i in range(num_records)],
        'latitude': np.random.uniform(19.0, 24.0, num_records), 
        'longitude': np.random.uniform(73.0, 79.0, num_records),
        'N': np.random.uniform(20, 140, num_records),
        'P': np.random.uniform(10, 100, num_records),
        'K': np.random.uniform(10, 200, num_records),
        'ph': np.random.uniform(5.5, 8.0, num_records),
        'historical_rainfall_mm': np.random.uniform(400, 1200, num_records)
    }
    return pd.DataFrame(data)

def generate_mandi_data(days=365):
    np.random.seed(42)
    dates = [datetime.now() - timedelta(days=x) for x in range(days)]
    commodities = ['Onion', 'Potato', 'Cotton', 'Soyabean']
    mandis = ['Lasalgaon', 'Pune', 'Nagpur', 'Indore']
    
    records = []
    for dt in dates:
        for mandi in mandis:
            for comm in commodities:
                base_price = 1500 if comm=='Potato' else 2200 if comm=='Onion' else 5000
                noise = np.random.normal(0, 150)
                records.append({
                    'date': dt.strftime('%Y-%m-%d'),
                    'mandi_name': mandi,
                    'commodity': comm,
                    'modal_price_q': max(800, int(base_price + noise))
                })
    return pd.DataFrame(records)
