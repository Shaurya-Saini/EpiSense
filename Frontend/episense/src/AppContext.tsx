import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from "react";
import type { SensorReading } from "./types";

const WS_URL = "ws://localhost:8000/ws";
const API_URL = "http://localhost:8000/api";

interface AppContextType {
  readings: SensorReading[];
  zoneUpdates: Record<string, any>;
  alerts: any[];
  symptomReports: any[];
  connected: boolean;
  refreshSymptomReports: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useAppContext = () => {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppContext must be used within AppProvider");
  return ctx;
};

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [zoneUpdates, setZoneUpdates] = useState<Record<string, any>>({});
  const [alerts, setAlerts] = useState<any[]>([]);
  const [symptomReports, setSymptomReports] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchInitialData = useCallback(async () => {
    try {
      // Fetch Readings
      const resR = await fetch(`${API_URL}/readings`);
      if (resR.ok) setReadings((await resR.json()).slice(0, 50));

      // Fetch Zones
      const resZ = await fetch(`${API_URL}/zones`);
      if (resZ.ok) {
        const zones = await resZ.json();
        const zMap: Record<string, any> = {};
        zones.forEach((z: any) => zMap[z.zone_id] = z);
        setZoneUpdates(zMap);
      }

      // Fetch Symptom Reports
      const resS = await fetch(`${API_URL}/symptom-reports`);
      if (resS.ok) setSymptomReports((await resS.json()).slice(0, 50));
    } catch (e) {
      console.warn("[EpiSense] Could not fetch initial state.", e);
    }
  }, []);

  const refreshSymptomReports = useCallback(async () => {
      try {
          const res = await fetch(`${API_URL}/symptom-reports`);
          if (res.ok) setSymptomReports((await res.json()).slice(0, 50));
      } catch(e) {}
  }, []);

  const connectWs = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "ZONE_UPDATE" || data.ori !== undefined) {
          setZoneUpdates(prev => ({ ...prev, [data.zone_id]: data }));
          if (data.latest_reading) {
            setReadings(prev => [data.latest_reading, ...prev].slice(0, 50));
          }
          if (data.alerts && (data.alerts.level === "Warning" || data.alerts.level === "Critical")) {
            setAlerts(prev => {
              const newAlerts = [{...data.alerts, zone_id: data.zone_id, time: new Date().toLocaleTimeString()}, ...prev];
              return newAlerts.slice(0, 5);
            });
          }
          // Also refresh symptom reports periodically if a zone update triggered due to a symptom
          refreshSymptomReports();
        } else {
          setReadings((prev) => [data, ...prev].slice(0, 50));
        }
      } catch (err) {}
    };

    ws.onclose = () => {
      setConnected(false);
      reconnectTimer.current = setTimeout(connectWs, 3000);
    };

    ws.onerror = () => ws.close();
    wsRef.current = ws;
  }, [refreshSymptomReports]);

  useEffect(() => {
    fetchInitialData();
    connectWs();
    return () => {
      wsRef.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [fetchInitialData, connectWs]);

  return (
    <AppContext.Provider value={{ readings, zoneUpdates, alerts, symptomReports, connected, refreshSymptomReports }}>
      {children}
    </AppContext.Provider>
  );
};
