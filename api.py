from fastapi import FastAPI, BackgroundTasks, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator
import os
import asyncio
from typing import List
from data_pipeline import generate_farmer_field_data, generate_mandi_data
from models import MLPredictiveEngine
from optimizer import compute_optimal_strategy
from clustering import generate_procurement_hubs
from database import init_db, save_farm_record, fetch_all_farm_records, purge_all_database_records
from logger import app_logger  # NEW IMPORT
import urllib.request

app = FastAPI(title="AgriIntel Platform API (Production Candidate)")

# Define your project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

# Create the static directory if it doesn't exist
os.makedirs(static_dir, exist_ok=True)

# Define Leaflet URLs to download from
# leaflet_assets = {
#     "leaflet.js": "https://unpkg.com",
#     "leaflet.css": "https://unpkg.com"
# }

# # Automatically download files if they are missing from your static folder
# for file_name, url in leaflet_assets.items():
#     file_path = os.path.join(static_dir, file_name)
#     if not os.path.exists(file_path):
#         print(f"📦 Downloading missing asset: {file_name}...")
#         urllib.request.urlretrieve(url, file_path)
#         print(f"✅ Saved to {file_path}")


#Allow local HTML dashboards to read the JSON API pipelines securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any local file or dashboard engine to map vectors
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

# Mount the static file engine directory safely onto the backend routing tree
current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

templates = Jinja2Templates(directory=current_dir) 


@app.on_event("startup")
def on_startup():
    init_db()
    app_logger.info("Database initialized and Write-Ahead Logging (WAL) state verified.")

# Initialize and cache models within backend memory upon startup
ml_engine = MLPredictiveEngine()
df_fields = generate_farmer_field_data()
df_mandi = generate_mandi_data()
ml_engine.train_crop_recommender(df_fields)
app_logger.info("Ensemble Machine Learning Engines trained successfully.")

class AdvisoryRequest(BaseModel):
    farmer_id: str = Field(..., examples=["FARM_001"])
    latitude: float = Field(..., ge=6.0, le=37.0, examples=[19.87])
    longitude: float = Field(..., ge=68.0, le=98.0, examples=[75.34])
    acres: float = Field(default=2.5, ge=0.1, examples=[2.5])
    soil_profile: List[float] = Field(..., min_items=5, max_items=5, examples=[[95.0, 40.0, 120.0, 6.5, 850.0]])
    phone_number: str = Field(..., examples=["+919876543210"])

    @field_validator('soil_profile')
    @classmethod
    def validate_soil_metrics(cls, value: List[float]) -> List[float]:
        n, p, k, ph, rainfall = value
        if not (0 <= n <= 300) or not (0 <= p <= 150) or not (0 <= k <= 500) or not (3.5 <= ph <= 10.0) or not (0 <= rainfall <= 4000):
            app_logger.warning(f"Data Validation Blocked -> Soil parameters out of range: {value}")
            raise ValueError("Soil metric value scales breach valid agricultural bounds.")
        return value

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, value: str) -> str:
        clean_phone = value.replace(" ", "").replace("-", "")
        if (clean_phone.startswith("+91") and len(clean_phone) == 13) or (len(clean_phone) == 10 and clean_phone.isdigit()):
            return clean_phone if clean_phone.startswith("+91") else f"+91{clean_phone}"
        app_logger.warning(f"Data Validation Blocked -> Invalid routing telephone string: {value}")
        raise ValueError("Invalid phone number format.")

def send_low_bandwidth_sms(request: AdvisoryRequest):
    import time
    time.sleep(0.1) 
    
    app_logger.info(f"Processing advisory matrix computations for Farmer ID: {request.farmer_id}")
    plan = compute_optimal_strategy(request.soil_profile, request.latitude, request.longitude, df_mandi, ml_engine)
    
    save_farm_record(
        farmer_id=request.farmer_id,
        lat=request.latitude,
        lon=request.longitude,
        acres=request.acres,
        crop=plan['recommended_crop']
    )
    
    sms_text = f"Kisan Alert: Grow {plan['recommended_crop']}. Best Market: {plan['target_mandi']}."
    app_logger.info(f"Transaction logged to DB disk sector. Outbound SMS triggered for {request.phone_number}.")

# Ensure your root route forces the browser to discard old cached content

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    html_path = "index.html"
    if os.path.exists(html_path):
        return templates.TemplateResponse(
            request=request,
            name="index.html", 
            context={},
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return HTMLResponse(content="<h1>AgriIntel Server Online (HTML File Missing)</h1>")


@app.get("/v1/system/status")
async def get_system_status_json():
    """Returns structured system telemetry cleanly to terminal scripts."""
    historical_ledger = fetch_all_farm_records()
    return {
        "status": "online",
        "total_persistent_records": len(historical_ledger)
    }

@app.post("/v1/advisory/async")
async def request_advisory_async(payload: AdvisoryRequest, background_tasks: BackgroundTasks):
    app_logger.info(f"Inbound telemetry hit received for target edge tracker ID: {payload.farmer_id}")
    background_tasks.add_task(send_low_bandwidth_sms, payload)
    return {"status": "queued"}

@app.get("/v1/logistics/hubs")
async def get_procurement_hubs():
    historical_ledger = fetch_all_farm_records()
    hubs = generate_procurement_hubs(historical_ledger)
    app_logger.info(f"Geospatial DBSCAN query generated. Active supply hubs built: {len(hubs)}")
    return {"active_hubs_count": len(hubs), "procurement_hubs": hubs}

# Triggers programmatic cleanup array over the network
@app.post("/v1/system/purge", status_code=status.HTTP_200_OK)
async def clear_system_database():
    app_logger.critical("SYSTEM PURGE REQUEST DETECTED: Executing global database reset workflow.")
    success = purge_all_database_records()
    if not success:
        raise HTTPException(status_code=500, detail="Database engine failed to delete active records row index clusters.")
    return {"status": "success", "message": "All historical ledger entries permanently dropped."}
