"""
EpiSense Backend — FastAPI Application

Provides REST endpoints for sensor data ingestion and a WebSocket
endpoint for real-time dashboard streaming.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import List
import math
import math

from app.schemas import SensorData, SensorResponse, ReadingRecord, SymptomReportData, SymptomReportRecord, ZoneUpdate, AlertTier
from app.ml_model import load_model, predict_risk
from app.data_store import store
from app.disease_engine import determine_alert_tier, match_diseases

# ── App Initialization ──────────────────────────────────────────────
app = FastAPI(
    title="EpiSense API",
    description="IoT-based environmental sensing backend for disease outbreak risk prediction",
    version="1.0.0",
)

# CORS — allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── WebSocket Connection Manager ────────────────────────────────────
class ConnectionManager:
    """Manages active WebSocket connections for live broadcasting."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.active_connections.remove(connection)


manager = ConnectionManager()

# ── Startup Event ────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Load the ML model when the server starts."""
    load_model()
    print("[INFO] EpiSense Backend is running.")

def get_e_score(reading: dict) -> float:
    # potability = 0 means unsafe. potability = 1 means safe.
    confidence = reading.get("confidence", 0)
    potability = reading.get("potability", 1)
    if potability == 0:
        return confidence
    else:
        return 1.0 - confidence

def get_s_score_decayed(report: dict) -> float:
    if not report:
        return 0.0
    timestamp = report.get("timestamp")
    try:
        report_time = datetime.fromisoformat(timestamp)
        now = datetime.now(timezone.utc)
        hours_since = (now - report_time).total_seconds() / 3600.0
        s_score = report.get("s_score", 0.0)
        # S_score_decayed = S_score * e^(−λ * hours_since_report)
        return s_score * math.exp(-0.03 * max(0, hours_since))
    except Exception:
        return 0.0

async def trigger_ori_recomputation(zone_id: str):
    latest_reading = store.get_latest_reading_for_zone(zone_id)
    latest_report = store.get_latest_report_for_zone(zone_id)

    e_score = get_e_score(latest_reading) if latest_reading else 0.0
    s_score_decayed = get_s_score_decayed(latest_report) if latest_report else 0.0

    # ORI = α × E_score + β × S_score (default: α = 0.55, β = 0.45)
    ori = 0.55 * e_score + 0.45 * s_score_decayed

    alert_level = determine_alert_tier(ori)
    matched_diseases_profiles = match_diseases(ori, e_score, latest_reading, latest_report)
    
    diseases = [dp["name"] for dp in matched_diseases_profiles]
    precautions = []
    for dp in matched_diseases_profiles:
        precautions.extend(dp["precautions"])
    precautions = list(set(precautions))

    alert_tier = AlertTier(level=alert_level, diseases=diseases, precautions=precautions)

    zone_update = ZoneUpdate(
        zone_id=zone_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        e_score=e_score,
        s_score_decayed=s_score_decayed,
        ori=ori,
        alerts=alert_tier,
        latest_reading=latest_reading
    )

    await manager.broadcast(zone_update.dict())

# ── REST Endpoints ───────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "EpiSense Backend"}


@app.post("/api/sensor-data", response_model=SensorResponse)
async def ingest_sensor_data(data: SensorData):
    """
    Receive sensor data from ESP32, run ML prediction,
    store the reading, and broadcast to WebSocket clients.
    """
    # Run prediction
    risk_level, confidence, potability = predict_risk(
        tds=data.tds,
        turbidity=data.turbidity,
        temperature=data.temperature,
    )

    # Build reading record
    reading = {
        "zone_id": data.zone_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tds": data.tds,
        "turbidity": data.turbidity,
        "temperature": data.temperature,
        "risk_level": risk_level,
        "confidence": round(confidence, 4),
        "potability": potability,
    }

    # Store in memory
    stored = store.add_reading(reading)

    await trigger_ori_recomputation(data.zone_id)

    return SensorResponse(status="ok", reading=ReadingRecord(**stored))

@app.post("/api/symptom-report", response_model=SymptomReportRecord)
async def ingest_symptom_report(data: SymptomReportData):
    # Calculate s_score
    raw_symptom_burden = (data.fever * 0.4) + (data.diarrhea * 0.35) + (data.vomiting * 0.15) + (data.rash * 0.05) + (data.respiratory * 0.05)
    s_score = min(raw_symptom_burden / max(1, data.population), 1.0)
    
    report = {
        "zone_id": data.zone_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "population": data.population,
        "fever": data.fever,
        "diarrhea": data.diarrhea,
        "vomiting": data.vomiting,
        "rash": data.rash,
        "respiratory": data.respiratory,
        "s_score": s_score
    }
    
    stored = store.add_symptom_report(report)
    
    await trigger_ori_recomputation(data.zone_id)
    
    return SymptomReportRecord(**stored)

@app.get("/api/readings", response_model=List[ReadingRecord])
async def get_readings():
    """Return the most recent 50 sensor readings across all zones."""
    readings = store.get_readings(limit=50)
    return [ReadingRecord(**r) for r in readings]

@app.get("/api/ori-status/{zone_id}")
async def get_ori_status(zone_id: str):
    """Return current ORI for a specific zone."""
    latest_reading = store.get_latest_reading_for_zone(zone_id)
    latest_report = store.get_latest_report_for_zone(zone_id)

    e_score = get_e_score(latest_reading) if latest_reading else 0.0
    s_score_decayed = get_s_score_decayed(latest_report) if latest_report else 0.0

    ori = 0.55 * e_score + 0.45 * s_score_decayed
    return {
        "zone_id": zone_id,
        "ori": ori,
        "e_score": e_score,
        "s_score_decayed": s_score_decayed
    }

@app.get("/api/symptom-reports", response_model=List[SymptomReportRecord])
async def get_symptom_reports():
    reports = store.get_symptom_reports(limit=50)
    return [SymptomReportRecord(**r) for r in reports]

@app.get("/api/zones", response_model=List[ZoneUpdate])
async def get_all_zones_status():
    zones = store.get_all_zones()
    status_list = []
    for z in zones:
        latest_reading = store.get_latest_reading_for_zone(z)
        latest_report = store.get_latest_report_for_zone(z)
        
        e_score = get_e_score(latest_reading) if latest_reading else 0.0
        s_score_decayed = get_s_score_decayed(latest_report) if latest_report else 0.0
        ori = 0.55 * e_score + 0.45 * s_score_decayed
        
        alert_level = determine_alert_tier(ori)
        matched_diseases_profiles = match_diseases(ori, e_score, latest_reading, latest_report)
        diseases = [dp["name"] for dp in matched_diseases_profiles]
        precautions = []
        for dp in matched_diseases_profiles:
            precautions.extend(dp["precautions"])
        precautions = list(set(precautions))

        alert_tier = AlertTier(level=alert_level, diseases=diseases, precautions=precautions)
        
        status_list.append(ZoneUpdate(
            zone_id=z,
            timestamp=datetime.now(timezone.utc).isoformat(),
            e_score=e_score,
            s_score_decayed=s_score_decayed,
            ori=ori,
            alerts=alert_tier,
            latest_reading=latest_reading
        ))
    return status_list


# ── WebSocket Endpoint ───────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard streaming.
    Clients connect here to receive live sensor data broadcasts.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive — listen for client messages (e.g., pings)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
