# EpiSense — Setup & Run Instructions

Complete guide to setting up and running every layer of the EpiSense system.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Backend server & ML training |
| Node.js | 18+ | Frontend development server |
| npm | 9+ | Frontend package manager |
| Arduino IDE | 2.x | ESP32 firmware flashing |
| Git | any | Version control |

---

## 1. Backend Setup

### 1.1 Create a Virtual Environment

Open a terminal inside the `Backend/` directory:

```bash
cd Backend
python -m venv venv
```

### 1.2 Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.4 Train the ML Model

Before running the server, you need to train and save the model.

1. **Download the dataset:**
   - Go to [Kaggle — Water Potability Dataset](https://www.kaggle.com/datasets/adityakadiwal/water-potability)
   - Download `water_potability.csv`
   - Place the file at: `Backend/data/water_potability.csv`

2. **Run the training script:**
   ```bash
   python train_model.py
   ```
   This will train an XGBoost classifier and save it to `Backend/model/model.joblib`.

> **Note:** If you skip this step, the backend will still run using a rule-based fallback predictor. The ML model simply provides better accuracy.

### 1.5 Start the Backend Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at:
- **REST API docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/api/health
- **WebSocket:** ws://localhost:8000/ws

### 1.6 Test with Sample Data

You can send a test reading using **curl** or the Swagger UI at `/docs`:

```bash
curl -X POST http://localhost:8000/api/sensor-data \
  -H "Content-Type: application/json" \
  -d "{\"tds\": 450.5, \"turbidity\": 3.2, \"temperature\": 27.8}"
```

---

## 2. Frontend Setup

### 2.1 Install Dependencies

Open a terminal inside the `Frontend/episense/` directory:

```bash
cd Frontend/episense
npm install
npm install react-router-dom leaflet react-leaflet leaflet.heat @types/leaflet @types/leaflet.heat
```

### 2.2 Start Development Server

```bash
npm run dev
```

The dashboard will be available at: **http://localhost:5173**

### 2.3 Build for Production (Optional)

```bash
npm run build
```

The production build will be output to `Frontend/episense/dist/`.

### 2.4 Configuration

The frontend connects to the backend at `ws://localhost:8000/ws` by default.

To change this, edit the constants at the top of `Frontend/episense/src/App.tsx`:

```typescript
const WS_URL = "ws://localhost:8000/ws";
const API_URL = "http://localhost:8000/api";
```

---

## 3. Hardware Setup (ESP32)

### 3.1 Hardware Wiring

| Sensor | ESP32 Pin | Type |
|--------|-----------|------|
| TDS Sensor | GPIO 34 | Analog |
| Turbidity Sensor | GPIO 35 | Analog |
| DS18B20 Temperature | GPIO 4 | Digital (OneWire) |

### 3.2 Required Arduino Libraries

Install these via **Arduino IDE → Library Manager**:

- `ArduinoJson` (by Benoit Blanchon)
- `OneWire` (by Jim Studt)
- `DallasTemperature` (by Miles Burton)

### 3.3 Configure the Firmware

Open `Hardware/episense_firmware/episense_firmware.ino` in Arduino IDE and update:

```cpp
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://<YOUR_BACKEND_IP>:8000/api/sensor-data";
```

Replace `<YOUR_BACKEND_IP>` with the local IP address of the machine running the backend server.

### 3.4 Flash the Firmware

1. In Arduino IDE, select **Board → ESP32 Dev Module**
2. Select the correct **COM Port**
3. Click **Upload**

The ESP32 will begin reading sensors and sending data every 10 seconds.

---

## 4. Running the Full System

Start all components in this order:

1. **Backend** — `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` (from `Backend/`)
2. **Frontend** — `npm run dev` (from `Frontend/episense/`)
3. **ESP32** — Power on the flashed ESP32 board

The dashboard at http://localhost:5173 will show live sensor data as it arrives.

---

## 5. Project Structure

```
EpiSense/
├── Backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI server (REST + WebSocket)
│   │   ├── ml_model.py      # ML model loading & prediction
│   │   ├── schemas.py       # Pydantic request/response models
│   │   └── data_store.py    # In-memory reading storage
│   ├── data/                # Place water_potability.csv here
│   ├── model/               # Trained model output (model.joblib)
│   ├── train_model.py       # ML model training script
│   └── requirements.txt     # Python dependencies
├── Frontend/
│   └── episense/
│       ├── src/
│       │   ├── components/
│       │   │   ├── SensorCard.tsx
│       │   │   ├── RiskBadge.tsx
│       │   │   ├── SensorChart.tsx
│       │   │   └── HistoryTable.tsx
│       │   ├── App.tsx       # Main dashboard component
│       │   ├── App.css       # Dashboard styles
│       │   ├── index.css     # Global styles & CSS variables
│       │   ├── types.ts      # TypeScript interfaces
│       │   └── main.tsx      # React entry point
│       ├── package.json
│       └── index.html
├── Hardware/
│   └── episense_firmware/
│       └── episense_firmware.ino  # ESP32 Arduino firmware
├── instructions.md           # ← You are here
└── ReadMe.md
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend: `Model file not found` | Run `python train_model.py` or skip — fallback predictor will be used |
| Frontend: WebSocket disconnected | Ensure the backend is running on port 8000 |
| ESP32: WiFi connection failed | Double-check SSID/password in the firmware |
| ESP32: POST failed | Verify the `SERVER_URL` IP matches the backend machine |
| CORS errors in browser | The backend allows all origins by default; ensure it is running |
