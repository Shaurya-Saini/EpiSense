"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SensorData(BaseModel):
    """Incoming sensor data from ESP32."""
    tds: float = Field(..., description="Total Dissolved Solids (ppm)")
    turbidity: float = Field(..., description="Turbidity (NTU)")
    temperature: float = Field(..., description="Water temperature (°C)")


class PredictionResult(BaseModel):
    """ML model prediction output."""
    risk_level: str = Field(..., description="Risk classification: Low, Medium, or High")
    confidence: float = Field(..., description="Prediction confidence score (0-1)")
    potability: int = Field(..., description="Water potability prediction (0 or 1)")


class ReadingRecord(BaseModel):
    """A single stored reading with sensor data, prediction, and timestamp."""
    id: int
    timestamp: str
    tds: float
    turbidity: float
    temperature: float
    risk_level: str
    confidence: float
    potability: int


class SensorResponse(BaseModel):
    """Response returned after ingesting sensor data."""
    status: str
    reading: ReadingRecord
