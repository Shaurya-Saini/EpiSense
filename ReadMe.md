# EpiSense

Real-time disease outbreak prediction using IoT environmental sensors and machine learning.

## What It Does

Monitors water quality parameters (TDS, turbidity, temperature) via IoT sensors, analyzes them with an ML model, and displays live risk predictions on a web dashboard.

## Tech Stack

- **Hardware:** ESP32 + TDS, turbidity, and temperature sensors
- **Backend:** Python, FastAPI, WebSocket
- **ML:** XGBoost trained on [Kaggle Water Potability Dataset](https://www.kaggle.com/datasets/adityakadiwal/water-potability)
- **Frontend:** React, TypeScript, Recharts, Vite

## Quick Start

See **[instructions.md](./instructions.md)** for full setup and run commands.

## Architecture

```
Sensors → ESP32 → REST API → FastAPI + ML Model → WebSocket → React Dashboard
```

## License

MIT