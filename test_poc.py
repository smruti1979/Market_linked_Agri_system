from data_pipeline import generate_farmer_field_data, generate_mandi_data
from models import MLPredictiveEngine
from optimizer import compute_optimal_strategy

def run_local_poc_test():
    print("Initializing PoC Pipeline Components...")
    df_fields = generate_farmer_field_data()
    df_mandi = generate_mandi_data()
    
    print("Training Intelligent Machine Learning models...")
    engine = MLPredictiveEngine()
    engine.train_crop_recommender(df_fields)
    
    # Mock parameters representing a typical smallholder profile in Maharashtra/Vidarbha
    test_soil = [95.0, 40.0, 120.0, 6.5, 850.0]  # N, P, K, pH, Rainfall
    test_lat = 19.87
    test_lon = 75.34
    
    print("Running Optimization Core Engine...")
    result = compute_optimal_strategy(test_soil, test_lat, test_lon, df_mandi, engine)
    
    print("\n=== SYSTEM OPTIMIZATION ADVISORY RESULT ===")
    for key, val in result.items():
        print(f"{key.replace('_', ' ').title()}: {val}")
    print("===========================================")

if __name__ == "__main__":
    run_local_poc_test()