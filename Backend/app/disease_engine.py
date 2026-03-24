import json
from typing import List, Dict, Any

DISEASE_PROFILES = [
    {
        "name": "Cholera / Typhoid",
        "conditions": {
            "environmental": ["High Turbidity", "High TDS"],
            "symptoms": ["diarrhea", "vomiting"]
        },
        "precautions": ["Boil water before use", "Deploy water purification tablets"]
    },
    {
        "name": "Dengue / Malaria",
        "conditions": {
            "environmental": ["High Temperature"],
            "symptoms": ["fever", "rash"]
        },
        "precautions": ["Deploy mosquito fogging", "Clear stagnant water"]
    },
    {
        "name": "Respiratory Infection",
        "conditions": {
            "environmental": [],
            "symptoms": ["respiratory", "fever"]
        },
        "precautions": ["Distribute masks", "Advise vulnerable populations to stay indoors"]
    }
]

def determine_alert_tier(ori: float) -> str:
    if ori >= 0.8:
        return "Critical"
    elif ori >= 0.6:
        return "Warning"
    elif ori >= 0.4:
        return "Advisory"
    return "Normal"

def match_diseases(ori: float, e_score: float, latest_reading: Dict[str, Any], latest_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    if ori < 0.4:
        return []

    matched = []
    env_flags = []
    
    if latest_reading:
        if latest_reading.get("turbidity", 0) > 5:
            env_flags.append("High Turbidity")
        if latest_reading.get("tds", 0) > 800:
            env_flags.append("High TDS")
        if latest_reading.get("temperature", 0) > 35:
            env_flags.append("High Temperature")
            
    symp_flags = []
    if latest_report:
        if latest_report.get("diarrhea", 0) > 0: symp_flags.append("diarrhea")
        if latest_report.get("vomiting", 0) > 0: symp_flags.append("vomiting")
        if latest_report.get("fever", 0) > 0: symp_flags.append("fever")
        if latest_report.get("rash", 0) > 0: symp_flags.append("rash")
        if latest_report.get("respiratory", 0) > 0: symp_flags.append("respiratory")

    for dp in DISEASE_PROFILES:
        env_match = any(e in env_flags for e in dp["conditions"]["environmental"]) or not dp["conditions"]["environmental"]
        symp_match = any(s in symp_flags for s in dp["conditions"]["symptoms"]) or not dp["conditions"]["symptoms"]
        
        if env_match and symp_match:
            matched.append(dp)

    return matched

