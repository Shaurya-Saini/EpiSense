"""Machine learning model loading and prediction utilities."""

import os
import joblib
import numpy as np
from typing import Tuple

# Path to the saved model and pipeline files
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
PIPELINE_PATH = os.path.join(MODEL_DIR, "pipeline.joblib")

_model = None
_pipeline = None


def load_model():
    """Load the trained ML model and preprocessing pipeline from disk."""
    global _model, _pipeline

    if not os.path.exists(MODEL_PATH):
        print(f"[WARNING] Model file not found at {MODEL_PATH}. Using fallback rule-based prediction.")
        _model = None
        _pipeline = None
        return

    _model = joblib.load(MODEL_PATH)
    print(f"[INFO] ML model loaded successfully from {MODEL_PATH}")

    if os.path.exists(PIPELINE_PATH):
        _pipeline = joblib.load(PIPELINE_PATH)
        print(f"[INFO] Preprocessing pipeline loaded from {PIPELINE_PATH}")
    else:
        _pipeline = None
        print("[WARNING] Pipeline file not found. Raw features will be passed directly to model.")


def predict_risk(tds: float, turbidity: float, temperature: float) -> Tuple[str, float, int]:
    """
    Predict outbreak risk based on sensor readings.

    The model expects 3 features in this order: [Solids, Turbidity, ph]
    Sensor mapping:
        - TDS sensor       → Solids
        - Turbidity sensor  → Turbidity
        - Temperature sensor → ph (proxy)

    Returns:
        Tuple of (risk_level, confidence, potability)
        - risk_level: "Low", "Medium", or "High"
        - confidence: float between 0 and 1
        - potability: 0 (not potable / risky) or 1 (potable / safe)
    """
    if _model is not None:
        # Build raw feature array: [Solids, Turbidity, ph]
        features = np.array([[tds, turbidity, temperature]])

        # Apply preprocessing pipeline if available
        if _pipeline is not None:
            imputer = _pipeline["imputer"]
            scaler = _pipeline["scaler"]
            features = imputer.transform(features)
            features = scaler.transform(features)

        prediction = _model.predict(features)[0]
        probabilities = _model.predict_proba(features)[0]
        confidence = float(np.max(probabilities))
        potability = int(prediction)
    else:
        # Fallback: rule-based heuristic when no model is available
        potability, confidence = _rule_based_prediction(tds, turbidity, temperature)

    # Map potability to risk level with confidence-based granularity
    risk_level = _map_to_risk_level(potability, confidence, tds, turbidity, temperature)

    return risk_level, confidence, potability


def _rule_based_prediction(tds: float, turbidity: float, temperature: float) -> Tuple[int, float]:
    """
    Simple rule-based fallback when no ML model is available.
    Based on WHO water quality guidelines.
    """
    risk_score = 0.0

    # TDS assessment (WHO recommends < 500 ppm)
    if tds > 1000:
        risk_score += 0.4
    elif tds > 500:
        risk_score += 0.2

    # Turbidity assessment (WHO recommends < 4 NTU)
    if turbidity > 5:
        risk_score += 0.4
    elif turbidity > 4:
        risk_score += 0.2

    # Temperature assessment (higher temps can promote pathogen growth)
    if temperature > 35:
        risk_score += 0.2
    elif temperature > 30:
        risk_score += 0.1

    potability = 0 if risk_score >= 0.4 else 1
    confidence = min(0.5 + risk_score, 0.95)

    return potability, confidence


def _map_to_risk_level(
    potability: int, confidence: float,
    tds: float, turbidity: float, temperature: float
) -> str:
    """Map prediction output to a human-readable risk level."""
    if potability == 1:
        # Water is predicted safe
        return "Low"
    else:
        # Water is predicted unsafe — determine severity
        danger_indicators = 0
        if tds > 800:
            danger_indicators += 1
        if turbidity > 5:
            danger_indicators += 1
        if temperature > 35:
            danger_indicators += 1

        if danger_indicators >= 2 or confidence > 0.8:
            return "High"
        else:
            return "Medium"
