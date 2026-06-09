import pandas as pd
import requests
import time
from sklearn.cluster import DBSCAN
from config import CLUSTER_RADIUS_DEGREES, MIN_FARMS_PER_HUB, CROP_ECONOMICS

# NEW: Local caching layer to block outbound port throttling during concurrent stress tests
GEOLOCATION_CACHE = {}

def get_location_name(lat, lon):
    """Translates GPS coordinates into place names with active safety caching mechanisms."""
    # Round coordinates slightly to create a regional zone bucket cache
    cache_key = (round(lat, 2), round(lon, 2))
    if cache_key in GEOLOCATION_CACHE:
        return GEOLOCATION_CACHE[cache_key]

    url = f"https://openstreetmap.org{lat}&lon={lon}&format=json&zoom=10"
    headers = {'User-Agent': 'AgriIntelPlatformPoC_Hardened/2.0'}
    
    try:
        # Prevent hammering public servers under stress test conditions
        response = requests.get(url, headers=headers, timeout=2.5)
        if response.status_code == 200:
            address = response.json().get('address', {})
            district = address.get('district') or address.get('county') or address.get('state_district')
            state = address.get('state')
            
            if district and state:
                name = f"{district}, {state}"
            elif state:
                name = f"{state} Region"
            else:
                name = "Rural Mandi Cluster"
                
            # Store in cache to shield subsequent worker thread passes
            GEOLOCATION_CACHE[cache_key] = name
            return name
    except Exception:
        pass
        
    return "Central India Hub"

def generate_procurement_hubs(active_farmers_list):
    if not active_farmers_list or len(active_farmers_list) < MIN_FARMS_PER_HUB:
        return []

    df = pd.DataFrame(active_farmers_list)
    all_hubs = []

    for crop in df['recommended_crop'].unique():
        df_crop = df[df['recommended_crop'] == crop].copy()
        if len(df_crop) < MIN_FARMS_PER_HUB:
            continue
            
        coords = df_crop[['latitude', 'longitude']].values
        db = DBSCAN(eps=CLUSTER_RADIUS_DEGREES, min_samples=MIN_FARMS_PER_HUB, metric='euclidean')
        df_crop['cluster_id'] = db.fit_predict(coords)
        
        df_valid_clusters = df_crop[df_crop['cluster_id'] != -1]
        if df_valid_clusters.empty:
            continue

        per_acre_yield = CROP_ECONOMICS[crop]['yield_q']
        
        hub_summary = df_valid_clusters.groupby('cluster_id').agg(
            hub_latitude=('latitude', 'mean'),
            hub_longitude=('longitude', 'mean'),
            total_farmers=('farmer_id', 'count'),
            total_acres=('acres', 'sum')
        ).reset_index()
        
        records = hub_summary.to_dict(orient='records')
        for row in records:
            lat = round(float(row['hub_latitude']), 4)
            lon = round(float(row['hub_longitude']), 4)
            
            # Fetch names via cached lookup
            place_name = get_location_name(lat, lon)
            
            total_yield = round(float(row['total_acres'] * per_acre_yield), 2)
            all_hubs.append({
                "crop": crop,
                "hub_id": f"HUB_{crop.upper()}_{int(row['cluster_id'])}",
                "center_latitude": lat,
                "center_longitude": lon,
                "location_name": place_name,
                "farmer_density": int(row['total_farmers']),
                "projected_yield_quintals": total_yield
            })
            
    return all_hubs
