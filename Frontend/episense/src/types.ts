/**
 * TypeScript interfaces for the EpiSense dashboard.
 */

/** A single sensor reading received from the backend. */
export interface SensorReading {
  id: number;
  timestamp: string;
  tds: number;
  turbidity: number;
  temperature: number;
  risk_level: "Low" | "Medium" | "High";
  confidence: number;
  potability: number;
}

/** Props for the SensorCard component. */
export interface SensorCardProps {
  label: string;
  value: number | null;
  unit: string;
  icon: string;
  color: string;
}

/** Props for the RiskBadge component. */
export interface RiskBadgeProps {
  riskLevel: "Low" | "Medium" | "High" | null;
  confidence: number | null;
}

/** Props for the SensorChart component. */
export interface SensorChartProps {
  readings: SensorReading[];
}

/** Props for the HistoryTable component. */
export interface HistoryTableProps {
  readings: SensorReading[];
}
