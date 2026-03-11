"""
EpiSense — ML Model Training Script

Trains an XGBoost classifier on water quality data to predict potability.
The trained model is saved to Backend/model/model.joblib for use by the
FastAPI server at runtime.

Dataset: Kaggle Water Potability Dataset
    https://www.kaggle.com/datasets/adityakadiwal/water-potability

Usage:
    python train_model.py
    (Run from the Backend/ directory)
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier
import joblib

# ── Configuration ────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "water_potability.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")

# Features used by the model (must match the sensor inputs)
# The Kaggle dataset has: ph, Hardness, Solids, Chloramines, Sulfate,
# Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Potability
#
# We map our sensors to dataset columns:
#   TDS         →  Solids
#   Turbidity   →  Turbidity
#   Temperature →  ph (used as proxy; in production, retrain with real temp data)
FEATURE_COLUMNS = ["Solids", "Turbidity", "ph"]
TARGET_COLUMN = "Potability"


def load_data() -> pd.DataFrame:
    """Load and validate the water potability CSV dataset."""
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Dataset not found at: {DATA_PATH}")
        print(f"        Download it from: https://www.kaggle.com/datasets/adityakadiwal/water-potability")
        print(f"        Place the CSV file at: {DATA_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    print(f"[INFO] Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def preprocess(df: pd.DataFrame) -> tuple:
    """Select features, handle missing values, and split into train/test."""
    # Keep only the features we need
    required_cols = FEATURE_COLUMNS + [TARGET_COLUMN]
    for col in required_cols:
        if col not in df.columns:
            print(f"[ERROR] Missing required column: {col}")
            sys.exit(1)

    df = df[required_cols].copy()

    # Fill missing values with column medians
    df = df.fillna(df.median())

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].values

    # Split: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"[INFO] Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    print(f"[INFO] Class distribution — Train: {np.bincount(y_train)}, Test: {np.bincount(y_test)}")

    return X_train, X_test, y_train, y_test


def train(X_train, y_train) -> XGBClassifier:
    """Train an XGBoost classifier."""
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )

    model.fit(X_train, y_train)
    print("[INFO] Model training complete.")
    return model


def evaluate(model, X_test, y_test):
    """Evaluate the model and print metrics."""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n{'='*50}")
    print(f"  Model Accuracy: {accuracy:.4f}")
    print(f"{'='*50}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Not Potable (Risk)", "Potable (Safe)"]))


def save_model(model):
    """Save the trained model to disk."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"[INFO] Model saved to: {MODEL_PATH}")


def main():
    """Full training pipeline."""
    print("=" * 50)
    print("  EpiSense — ML Model Training")
    print("=" * 50)
    print()

    df = load_data()
    X_train, X_test, y_train, y_test = preprocess(df)
    model = train(X_train, y_train)
    evaluate(model, X_test, y_test)
    save_model(model)

    print("\n[DONE] Training pipeline complete. Model is ready for deployment.")


if __name__ == "__main__":
    main()
