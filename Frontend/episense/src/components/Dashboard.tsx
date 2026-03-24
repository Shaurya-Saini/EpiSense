import { useState } from "react";
import { Link } from "react-router-dom";
import SensorCard from "./SensorCard";
import RiskBadge from "./RiskBadge";
import SensorChart from "./SensorChart";
import HistoryTable from "./HistoryTable";
import HeatmapView from "./HeatmapView";
import { useAppContext } from "../AppContext";

const AVAILABLE_ZONES = ["zone_001", "zone_002", "zone_003"];

export default function Dashboard() {
  const { readings, zoneUpdates, alerts, symptomReports, connected } = useAppContext();
  const [activeZone, setActiveZone] = useState<string>("zone_001");

  // Filter data for the active zone
  const zoneReadings = readings.filter(r => r.zone_id === activeZone || r.zone_id === undefined); // fallback for old data without zone
  const zoneReports = symptomReports.filter(r => r.zone_id === activeZone);
  const activeZoneObj = zoneUpdates[activeZone] || {};
  const latestReading = zoneReadings.length > 0 ? zoneReadings[0] : null;

  return (
    <div className="app dashboard-container">
      {/* Header */}
      <header className="header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
           <h1 className="header__title">EpiSense Dashboard</h1>
           <p className="header__subtitle">Real-Time Environmental & Clinical Outbreak Tracking</p>
        </div>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
           <Link to="/clinic-upload" className="portal-btn">+ Add Clinical Report</Link>
           <div className={`header__status ${connected ? "header__status--connected" : "header__status--disconnected"}`}>
             <span className="status-dot" />
             {connected ? "Live System" : "Offline"}
           </div>
        </div>
      </header>

      {/* Global Alerts Banner */}
      {alerts.length > 0 && (
         <section className="alerts-section pulse-alert">
            <h3>⚠️ PUBLIC HEALTH ALERT ACTIVE</h3>
            <div className="alerts-list">
               {alerts.map((alert, i) => (
                  <div key={i} className="alert-item">
                     <strong>[{alert.time}] {alert.level.toUpperCase()} IN {alert.zone_id.toUpperCase()}</strong>
                     <span> | Probable Diseases: {alert.diseases?.join(", ")} | Precautions: {alert.precautions?.join("; ")}</span>
                  </div>
               ))}
            </div>
         </section>
      )}

      {/* Top Section: ORI Explainer & Map */}
      <div className="top-layout">
         <div className="ori-explainer-card">
            <h2 className="section-title" style={{ color: "var(--accent-cyan)" }}>Outbreak Risk Index (ORI)</h2>
            <p className="desc">
               The ORI is a unified geospatial health risk metric. It computationally fuses real-time water toxicity probabilities with community-driven syndromic surveillance to preemptively detect disease outbreak conditions.
            </p>
            <div className="formula-box">
                <div className="formula-main">ORI = α(E_Score) + β(S_Score)</div>
                <div className="sub-formulas">
                   <span><strong>E_Score:</strong> XGBoost Continuous Contamination Probability (Water Sensors)</span>
                   <span><strong>S_Score:</strong> S_initial × e^(-λt) (Decayed Localized Symptom Burden)</span>
                </div>
            </div>
         </div>
         <div className="map-view-hero">
            <h3 className="section-title" style={{ position: "absolute", zIndex: 10, padding: "1rem", pointerEvents: "none", margin: 0 }}>Global Risk Heatmap</h3>
            <HeatmapView zoneUpdates={zoneUpdates} />
         </div>
      </div>

      {/* Interactive Zone Selector (Tabs) */}
      <div className="tabs-container">
         {AVAILABLE_ZONES.map(z => (
            <button 
               key={z} 
               className={`tab-btn ${activeZone === z ? "active" : ""}`}
               onClick={() => setActiveZone(z)}
            >
               {z.replace("_", " ").toUpperCase()}
            </button>
         ))}
      </div>

      {/* Tab Content for Active Zone */}
      <div className="tab-content">
         
         <div className="zone-focus-header">
            <div className="zone-ori-display">
               <h3>Current ORI Index</h3>
               <div className="ori-big-number">{(activeZoneObj.ori || 0).toFixed(2)}</div>
               <div className="ori-breakdown">
                  <span>E_Score: <strong>{(activeZoneObj.e_score || 0).toFixed(2)}</strong></span>
                  <span>S_Score: <strong>{(activeZoneObj.s_score_decayed || 0).toFixed(2)}</strong></span>
               </div>
            </div>
            <div className="zone-risk-badge">
               <RiskBadge riskLevel={latestReading?.risk_level ?? null} confidence={latestReading?.confidence ?? null} />
            </div>
         </div>

         <div className="sensor-grid-horizontal" style={{ marginTop: "1.5rem" }}>
            <SensorCard label="Avg TDS" value={latestReading?.tds ?? null} unit="ppm" icon="💧" color="#06b6d4" />
            <SensorCard label="Avg Turbidity" value={latestReading?.turbidity ?? null} unit="NTU" icon="🌊" color="#a78bfa" />
            <SensorCard label="Avg Temp" value={latestReading?.temperature ?? null} unit="°C" icon="🌡️" color="#f97316" />
         </div>

         <div className="charts-and-logs">
            <div className="chart-sec">
               <SensorChart readings={zoneReadings} />
            </div>
            <div className="logs-sec">
               <div className="history-table">
                  <h3 className="section-title">Clinical Symptom History</h3>
                  {zoneReports.length === 0 ? (
                     <p className="no-data">No clinical reports for this zone yet.</p>
                  ) : (
                     <div className="history-table__scroll">
                        <table>
                           <thead>
                              <tr>
                                 <th>Date/Time</th>
                                 <th>Ppl</th>
                                 <th>Fever</th>
                                 <th>Diarrhea</th>
                                 <th>Vomiting</th>
                                 <th>Rasp</th>
                                 <th>Rash</th>
                                 <th>S_Score</th>
                              </tr>
                           </thead>
                           <tbody>
                              {zoneReports.map(r => (
                                 <tr key={r.id}>
                                    <td style={{ fontSize: '0.8rem' }}>{new Date(r.timestamp).toLocaleString()}</td>
                                    <td>{r.population}</td>
                                    <td style={{ color: r.fever > 0 ? "var(--accent-red)" : "inherit" }}>{r.fever}</td>
                                    <td style={{ color: r.diarrhea > 0 ? "var(--accent-amber)" : "inherit" }}>{r.diarrhea}</td>
                                    <td style={{ color: r.vomiting > 0 ? "var(--accent-orange)" : "inherit" }}>{r.vomiting}</td>
                                    <td style={{ color: r.respiratory > 0 ? "var(--accent-cyan)" : "inherit" }}>{r.respiratory}</td>
                                    <td style={{ color: r.rash > 0 ? "var(--accent-purple)" : "inherit" }}>{r.rash}</td>
                                    <td style={{ fontWeight: 'bold' }}>{(r.s_score || 0).toFixed(2)}</td>
                                 </tr>
                              ))}
                           </tbody>
                        </table>
                     </div>
                  )}
               </div>
            </div>
         </div>
         
         <div style={{ marginTop: "2rem" }}>
            <h3 className="section-title">Raw Sensor Stream</h3>
            <HistoryTable readings={zoneReadings} />
         </div>

      </div>
    </div>
  );
}
