import { useState, useEffect, useRef, useCallback } from "react";
import SensorCard from "./components/SensorCard";
import RiskBadge from "./components/RiskBadge";
import SensorChart from "./components/SensorChart";
import HistoryTable from "./components/HistoryTable";
import type { SensorReading } from "./types";
import "./App.css";

/** Backend config — update this if the server runs on a different host/port. */
const WS_URL = "ws://localhost:8000/ws";
const API_URL = "http://localhost:8000/api";

/** Max number of readings to keep in state for chart and table display. */
const MAX_READINGS = 30;

function App() {
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  /** Latest reading (most recent first). */
  const latest = readings.length > 0 ? readings[0] : null;

  // ── Fetch initial historical data ──────────────────────────────
  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/readings`);
      if (res.ok) {
        const data: SensorReading[] = await res.json();
        setReadings(data.slice(0, MAX_READINGS));
      }
    } catch {
      console.warn("[EpiSense] Could not fetch historical readings.");
    }
  }, []);

  // ── WebSocket connection with auto-reconnect ───────────────────
  const connectWs = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnected(true);
      console.log("[EpiSense] WebSocket connected.");
    };

    ws.onmessage = (event) => {
      try {
        const reading: SensorReading = JSON.parse(event.data);
        setReadings((prev) => [reading, ...prev].slice(0, MAX_READINGS));
      } catch (err) {
        console.error("[EpiSense] Failed to parse WebSocket message:", err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      console.log("[EpiSense] WebSocket disconnected. Reconnecting in 3s...");
      reconnectTimer.current = setTimeout(connectWs, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    fetchHistory();
    connectWs();

    return () => {
      wsRef.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [fetchHistory, connectWs]);

  // ── Render ─────────────────────────────────────────────────────
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1 className="header__title">EpiSense</h1>
        <p className="header__subtitle">
          Real-Time Environmental Monitoring &amp; Disease Outbreak Prediction Dashboard
        </p>
        <div
          className={`header__status ${connected ? "header__status--connected" : "header__status--disconnected"
            }`}
        >
          <span className="status-dot" />
          {connected ? "Live — Connected" : "Disconnected"}
        </div>
      </header>

      {/* Risk Badge */}
      <section className="risk-section">
        <RiskBadge
          riskLevel={latest?.risk_level ?? null}
          confidence={latest?.confidence ?? null}
        />
      </section>

      {/* Sensor Cards */}
      <section className="sensor-grid">
        <SensorCard
          label="Total Dissolved Solids"
          value={latest?.tds ?? null}
          unit="ppm"
          icon="💧"
          color="#06b6d4"
        />
        <SensorCard
          label="Turbidity"
          value={latest?.turbidity ?? null}
          unit="NTU"
          icon="🌊"
          color="#a78bfa"
        />
        <SensorCard
          label="Water Temperature"
          value={latest?.temperature ?? null}
          unit="°C"
          icon="🌡️"
          color="#f97316"
        />
      </section>

      {/* Real-Time Chart */}
      <SensorChart readings={readings} />

      {/* History Table */}
      <HistoryTable readings={readings} />
    </div>
  );
}

export default App;
