"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SensorData(BaseModel):
    """Incoming sensor data from ESP32."""
    tds: float = Field(..., description="Total Dissolved Solids (ppm)")
    turbidity: float = Field(..., description="Turbidity (NTU)")
    temperature: float = Field(..., description="Water temperature (°C)")
    zone_id: str = Field("zone_001", description="Identifier of the monitored zone")


class SymptomReportData(BaseModel):
    """Incoming clinic symptom report data."""
    zone_id: str
    population: int
    fever: int
    diarrhea: int
    vomiting: int
    rash: int
    respiratory: int


class PredictionResult(BaseModel):
    """ML model prediction output."""
    risk_level: str = Field(..., description="Risk classification: Low, Medium, or High")
    confidence: float = Field(..., description="Prediction confidence score (0-1)")
    potability: int = Field(..., description="Water potability prediction (0 or 1)")


class ReadingRecord(BaseModel):
    """A single stored reading with sensor data, prediction, and timestamp."""
    id: int
    zone_id: str
    timestamp: str
    tds: float
    turbidity: float
    temperature: float
    risk_level: str
    confidence: float
    potability: int


class SymptomReportRecord(BaseModel):
    """A single stored symptom report with calculated S_score."""
    id: int
    zone_id: str
    timestamp: str
    population: int
    fever: int
    diarrhea: int
    vomiting: int
    rash: int
    respiratory: int
    s_score: float


class AlertTier(BaseModel):
    level: str
    diseases: list[str]
    precautions: list[str]


class ZoneUpdate(BaseModel):
    """WebSocket update schema for a specific zone."""
    type: str = "ZONE_UPDATE"
    zone_id: str
    timestamp: str
    e_score: float
    s_score_decayed: float
    ori: float
    alerts: AlertTier
    latest_reading: Optional[ReadingRecord] = None


class SensorResponse(BaseModel):
    """Response returned after ingesting sensor data."""
    status: str
    reading: ReadingRecord
