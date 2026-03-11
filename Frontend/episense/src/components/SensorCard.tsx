import React from "react";
import type { SensorCardProps } from "../types";

const SensorCard: React.FC<SensorCardProps> = ({ label, value, unit, icon, color }) => {
    return (
        <div className="sensor-card" style={{ "--card-accent": color } as React.CSSProperties}>
            <div className="sensor-card__icon">{icon}</div>
            <div className="sensor-card__info">
                <span className="sensor-card__label">{label}</span>
                <div className="sensor-card__value-row">
                    <span className="sensor-card__value">
                        {value !== null ? value.toFixed(2) : "—"}
                    </span>
                    <span className="sensor-card__unit">{unit}</span>
                </div>
            </div>
            <div className="sensor-card__glow" />
        </div>
    );
};

export default SensorCard;
