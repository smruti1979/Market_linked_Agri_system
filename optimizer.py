import numpy as np
from config import MANDI_GEO, CROP_ECONOMICS, TRANSPORT_RATE_PER_KM_Q

def compute_optimal_strategy(soil_profile, lat, lon, df_mandi, ml_engine):
    # Fetch top agronomic crop options
    recommended_crops = ml_engine.predict_top_crops(soil_profile)
    
    best_strategy = {}
    max_net_profit = -float('inf')
    
    for crop in recommended_crops:
        econ = CROP_ECONOMICS[crop]
        
        for mandi, coords in MANDI_GEO.items():
            # Coordinate-to-distance conversion (~111km per spatial degree)
            distance = np.sqrt((lat - coords[0])**2 + (lon - coords[1])**2) * 111
            transport_cost = distance * TRANSPORT_RATE_PER_KM_Q * econ['yield_q']
            
            # Predict future crop value at market location
            predicted_price_per_q = ml_engine.forecast_mandi_price(df_mandi, mandi, crop)
            
            gross_revenue = predicted_price_per_q * econ['yield_q']
            net_profit = gross_revenue - econ['cost'] - transport_cost
            
            if net_profit > max_net_profit:
                max_net_profit = net_profit
                best_strategy = {
                    'recommended_crop': crop,
                    'target_mandi': mandi,
                    'projected_net_profit_per_acre': round(net_profit, 2),
                    'predicted_mandi_price': round(predicted_price_per_q, 2),
                    'estimated_logistics_cost': round(transport_cost, 2)
                }
                
    return best_strategy