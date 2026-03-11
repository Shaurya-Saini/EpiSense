import React from "react";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Legend,
} from "recharts";
import type { SensorChartProps, SensorReading } from "../types";

/** Format ISO timestamp to HH:MM:SS for chart axis labels. */
function formatTime(timestamp: string): string {
    try {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch {
        return timestamp;
    }
}

const SensorChart: React.FC<SensorChartProps> = ({ readings }) => {
    // Prepare data in chronological order (oldest first)
    const data = [...readings].reverse().map((r: SensorReading) => ({
        time: formatTime(r.timestamp),
        TDS: r.tds,
        Turbidity: r.turbidity,
        Temperature: r.temperature,
    }));

    if (data.length === 0) {
        return (
            <div className="chart-container chart-container--empty">
                <p>📊 No data yet — sensor readings will appear here in real time.</p>
            </div>
        );
    }

    return (
        <div className="chart-container">
            <h2 className="section-title">📈 Sensor Trends</h2>
            <ResponsiveContainer width="100%" height={320}>
                <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis
                        dataKey="time"
                        stroke="rgba(255,255,255,0.4)"
                        tick={{ fontSize: 11, fill: "rgba(255,255,255,0.5)" }}
                    />
                    <YAxis
                        stroke="rgba(255,255,255,0.4)"
                        tick={{ fontSize: 11, fill: "rgba(255,255,255,0.5)" }}
                    />
                    <Tooltip
                        contentStyle={{
                            background: "rgba(15, 23, 42, 0.95)",
                            border: "1px solid rgba(255,255,255,0.1)",
                            borderRadius: "12px",
                            color: "#e2e8f0",
                            fontSize: "13px",
                        }}
                    />
                    <Legend
                        wrapperStyle={{ fontSize: "13px", color: "#e2e8f0" }}
                    />
                    <Line
                        type="monotone"
                        dataKey="TDS"
                        stroke="#06b6d4"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 5 }}
                    />
                    <Line
                        type="monotone"
                        dataKey="Turbidity"
                        stroke="#a78bfa"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 5 }}
                    />
                    <Line
                        type="monotone"
                        dataKey="Temperature"
                        stroke="#f97316"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 5 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default SensorChart;
