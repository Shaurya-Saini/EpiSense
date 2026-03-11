import React from "react";
import type { HistoryTableProps, SensorReading } from "../types";

/** Format ISO timestamp to a readable local string. */
function formatTimestamp(timestamp: string): string {
    try {
        const date = new Date(timestamp);
        return date.toLocaleString([], {
            month: "short", day: "numeric",
            hour: "2-digit", minute: "2-digit", second: "2-digit",
        });
    } catch {
        return timestamp;
    }
}

const RISK_COLORS: Record<string, string> = {
    Low: "#22c55e",
    Medium: "#f59e0b",
    High: "#ef4444",
};

const HistoryTable: React.FC<HistoryTableProps> = ({ readings }) => {
    if (readings.length === 0) {
        return (
            <div className="history-table history-table--empty">
                <p>📋 No readings recorded yet.</p>
            </div>
        );
    }

    return (
        <div className="history-table">
            <h2 className="section-title">📋 Recent Readings</h2>
            <div className="history-table__scroll">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Timestamp</th>
                            <th>TDS (ppm)</th>
                            <th>Turbidity (NTU)</th>
                            <th>Temp (°C)</th>
                            <th>Risk</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {readings.map((r: SensorReading) => (
                            <tr key={r.id}>
                                <td className="history-table__id">{r.id}</td>
                                <td>{formatTimestamp(r.timestamp)}</td>
                                <td>{r.tds.toFixed(2)}</td>
                                <td>{r.turbidity.toFixed(2)}</td>
                                <td>{r.temperature.toFixed(2)}</td>
                                <td>
                                    <span
                                        className="history-table__risk"
                                        style={{ color: RISK_COLORS[r.risk_level] || "#94a3b8" }}
                                    >
                                        {r.risk_level}
                                    </span>
                                </td>
                                <td>{(r.confidence * 100).toFixed(1)}%</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default HistoryTable;
