"""
EpiSense Backend — FastAPI Application

Provides REST endpoints for sensor data ingestion and a WebSocket
endpoint for real-time dashboard streaming.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from typing import List

from app.schemas import SensorData, SensorResponse, ReadingRecord
from app.ml_model import load_model, predict_risk
from app.data_store import store

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

    # Broadcast to all connected dashboard clients
    await manager.broadcast(stored)

    return SensorResponse(status="ok", reading=ReadingRecord(**stored))


@app.get("/api/readings", response_model=List[ReadingRecord])
async def get_readings():
    """Return the most recent 50 sensor readings."""
    readings = store.get_readings(limit=50)
    return [ReadingRecord(**r) for r in readings]


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
