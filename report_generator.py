import os
from datetime import datetime
from database import fetch_all_farm_records
from clustering import generate_procurement_hubs

def generate_pickup_manifest():
    """
    Extracts database transaction ledgers, groups clusters,
    and writes out a text-based dispatch report file.
    """
    # 1. Fetch live entries from storage
    records = fetch_all_farm_records()
    hubs = generate_procurement_hubs(records)
    
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"pickup_manifest_{timestamp_str}.txt"
    
    # 2. Build string formatting layout
    report_content = []
    report_content.append("=========================================================================")
    report_content.append("               AGRIINTEL PLATFORM - BULK PROCUREMENT MANIFEST            ")
    report_content.append(f"               Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}             ")
    report_content.append("=========================================================================\n")
    report_content.append(f"Total Active Hubs Identified: {len(hubs)}")
    report_content.append(f"Total Contributing Farm Enclaves: {len(records)}\n")
    report_content.append("-------------------------------------------------------------------------")
    report_content.append(f"{'HUB ID':<15} | {'CROP':<10} | {'GPS CENTER':<20} | {'DENSITY':<8} | {'YIELD (Q)'}")
    report_content.append("-------------------------------------------------------------------------")
    
    total_volume = 0.0
    for hub in hubs:
        gps_str = f"{hub['center_latitude']},{hub['center_longitude']}"
        total_volume += hub['projected_yield_quintals']
        report_content.append(
            f"{hub['hub_id']:<15} | {hub['crop']:<10} | {gps_str:<20} | "
            f"{hub['farmer_density']:<8} | {hub['projected_yield_quintals']}"
        )
        
    report_content.append("-------------------------------------------------------------------------")
    report_content.append(f"TOTAL SYSTEM PROCUREMENT VOLUME: {round(total_volume, 2)} Quintals")
    report_content.append("=========================================================================\n")
    report_content.append("Logistics Instruction Notes:")
    report_content.append("1. Dispatch 10-Ton cargo vehicles to hubs breaking > 100 Quintals volume thresholds.")
    report_content.append("2. Coordinate regional direct-payment payouts upon field arrival confirmation.")
    report_content.append("\n*** END OF MANIFEST REPORT ***")
    
    # 3. Write out file safely
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(report_content))
        
    print(f"📦 Manifest compiled successfully: '{os.path.abspath(report_filename)}'")
    return report_filename

if __name__ == "__main__":
    # Ensure database has parameters before executing standalone test
    print("Scanning data records...")
    generate_pickup_manifest()
