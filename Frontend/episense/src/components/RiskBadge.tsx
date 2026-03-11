import React from "react";
import type { RiskBadgeProps } from "../types";

const RISK_CONFIG = {
    Low: { color: "#22c55e", bg: "rgba(34, 197, 94, 0.15)", label: "Low Risk", emoji: "✅" },
    Medium: { color: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)", label: "Medium Risk", emoji: "⚠️" },
    High: { color: "#ef4444", bg: "rgba(239, 68, 68, 0.15)", label: "High Risk", emoji: "🚨" },
};

const RiskBadge: React.FC<RiskBadgeProps> = ({ riskLevel, confidence }) => {
    if (!riskLevel) {
        return (
            <div className="risk-badge risk-badge--waiting">
                <span className="risk-badge__emoji">⏳</span>
                <span className="risk-badge__label">Awaiting Data</span>
            </div>
        );
    }

    const config = RISK_CONFIG[riskLevel];

    return (
        <div
            className={`risk-badge risk-badge--${riskLevel.toLowerCase()}`}
            style={{
                "--risk-color": config.color,
                "--risk-bg": config.bg,
            } as React.CSSProperties}
        >
            <span className="risk-badge__emoji">{config.emoji}</span>
            <div className="risk-badge__text">
                <span className="risk-badge__label">{config.label}</span>
                {confidence !== null && (
                    <span className="risk-badge__confidence">
                        Confidence: {(confidence * 100).toFixed(1)}%
                    </span>
                )}
            </div>
        </div>
    );
};

export default RiskBadge;
