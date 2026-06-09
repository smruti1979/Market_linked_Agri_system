# Regional geographic centers for coordinate estimation
MANDI_GEO = {
    'Lasalgaon': (20.14, 74.22),
    'Pune': (18.52, 73.85),
    'Nagpur': (21.14, 79.08),
    'Indore': (22.71, 75.85)
}

# Financial variables for economic calculations (Cost/Acre & Average Base Yields)
CROP_ECONOMICS = {
    'Potato': {'cost': 15000, 'yield_q': 15},
    'Cotton': {'cost': 25000, 'yield_q': 8},
    'Soyabean': {'cost': 18000, 'yield_q': 10},
    'Onion': {'cost': 20000, 'yield_q': 12}
}

CROP_VISUALS = {
    'Potato':  {'border': '#E65100', 'fill': '#FFB74D'},  # Orange Theme
    'Cotton':  {'border': '#455A64', 'fill': '#ECEFF1'},  # Slate/White Theme
    'Soyabean':{'border': '#F57F17', 'fill': '#FFF176'},  # Yellow Theme
    'Onion':   {'border': '#880E4F', 'fill': '#F06292'}   # Pink/Magenta Theme
}

TRANSPORT_RATE_PER_KM_Q = 4.5  # ₹4.5 per Kilometer per Quintal

# Geospatial Clustering Constants ---
# 0.18 degrees roughly corresponds to a ~20km search radius in India
CLUSTER_RADIUS_DEGREES = 0.18  
MIN_FARMS_PER_HUB = 3