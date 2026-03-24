"""Thread-safe SQLite data store for sensor readings and symptom reports."""

import sqlite3
import threading
import os
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "episense.db")

class SQLiteStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_conn(self):
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                tds REAL,
                turbidity REAL,
                temperature REAL,
                risk_level TEXT,
                confidence REAL,
                potability INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS symptom_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                population INTEGER,
                fever INTEGER,
                diarrhea INTEGER,
                vomiting INTEGER,
                rash INTEGER,
                respiratory INTEGER,
                s_score REAL
            )
        ''')
        conn.commit()
        conn.close()

    def add_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''
            INSERT INTO readings (zone_id, timestamp, tds, turbidity, temperature, risk_level, confidence, potability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reading.get("zone_id", "zone_001"),
            reading.get("timestamp"),
            reading.get("tds"),
            reading.get("turbidity"),
            reading.get("temperature"),
            reading.get("risk_level"),
            reading.get("confidence"),
            reading.get("potability")
        ))
        conn.commit()
        reading["id"] = c.lastrowid
        return reading

    def add_symptom_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''
            INSERT INTO symptom_reports (zone_id, timestamp, population, fever, diarrhea, vomiting, rash, respiratory, s_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.get("zone_id", "zone_001"),
            report.get("timestamp"),
            report.get("population"),
            report.get("fever"),
            report.get("diarrhea"),
            report.get("vomiting"),
            report.get("rash"),
            report.get("respiratory"),
            report.get("s_score")
        ))
        conn.commit()
        report["id"] = c.lastrowid
        return report

    def get_readings(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT * FROM readings ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in c.fetchall()]
        
    def get_symptom_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT * FROM symptom_reports ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in c.fetchall()]

    def get_latest_reading_for_zone(self, zone_id: str) -> Dict[str, Any] | None:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT * FROM readings WHERE zone_id = ? ORDER BY timestamp DESC LIMIT 1
        ''', (zone_id,))
        row = c.fetchone()
        return dict(row) if row else None

    def get_latest_report_for_zone(self, zone_id: str) -> Dict[str, Any] | None:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT * FROM symptom_reports WHERE zone_id = ? ORDER BY timestamp DESC LIMIT 1
        ''', (zone_id,))
        row = c.fetchone()
        return dict(row) if row else None

    def get_all_zones(self) -> List[str]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT DISTINCT zone_id FROM readings
            UNION
            SELECT DISTINCT zone_id FROM symptom_reports
        ''')
        return [row["zone_id"] for row in c.fetchall()]

store = SQLiteStore()
