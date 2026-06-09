import pandas as pd
from datetime import datetime
from data_pipeline import generate_mandi_data

def apply_seasonal_adjustments(df_mandi):
    """
    Applies realistic seasonal market variations based on the current month.
    - Onion/Potato: Prices dip during peak rabi harvest (Mar-May), rise in monsoon (Jul-Sep).
    - Cotton/Soyabean: Prices drop during kharif arrival market gluts (Oct-Dec).
    """
    current_month = datetime.now().month
    adjusted_records = []
    
    for _, row in df_mandi.iterrows():
        comm = row['commodity']
        price = row['modal_price_q']
        multiplier = 1.0
        
        if comm in ['Onion', 'Potato']:
            if current_month in [3, 4, 5]:    # Rabi harvest gluts
                multiplier = 0.80
            elif current_month in [7, 8, 9]:   # Rainy season scarcity
                multiplier = 1.35
        elif comm in ['Cotton', 'Soyabean']:
            if current_month in [10, 11, 12]: # Kharif harvest gluts
                multiplier = 0.85
            elif current_month in [5, 6, 7]:   # Pre-sowing scarcity
                multiplier = 1.20
                
        row['modal_price_q'] = max(600, int(price * multiplier))
        adjusted_records.append(row)
        
    return pd.DataFrame(adjusted_records)

if __name__ == "__main__":
    print("Fetching raw base data pipeline matrix...")
    df_raw = generate_mandi_data(days=30)
    
    print(f"Applying real-time seasonal scaling rules for Month: {datetime.now().strftime('%B')}...")
    df_adjusted = apply_seasonal_adjustments(df_raw)
    
    print("\nSample Data Points (Raw vs Seasonally Adjusted):")
    for comm in ['Onion', 'Cotton']:
        raw_p = df_raw[df_raw['commodity'] == comm]['modal_price_q'].iloc[0]
        adj_p = df_adjusted[df_adjusted['commodity'] == comm]['modal_price_q'].iloc[0]
        print(f"-> {comm}: Raw Base = ₹{raw_p}/Q | Adjusted = ₹{adj_p}/Q")
