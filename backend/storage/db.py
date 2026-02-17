import sqlite3
import os
import json
from typing import Optional
from models.data_model import NormalizedData
from models.alert_model import Alert


class Database:
    def __init__(self, db_path: Optional[str] = None):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(base, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = db_path or os.path.join(data_dir, "ocp_monitor.db")
        self.conn: Optional[sqlite3.Connection] = None

    def init_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                node_id TEXT,
                name TEXT,
                category TEXT,
                value TEXT,
                unit TEXT,
                timestamp INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                node_id TEXT,
                severity TEXT,
                message TEXT,
                value REAL,
                threshold REAL,
                timestamp INTEGER
            )
            """
        )
        self.conn.commit()

    def insert_measure(self, m: NormalizedData):
        if not self.conn:
            raise RuntimeError("Database not initialized")
        cur = self.conn.cursor()
        try:
            val_text = json.dumps(m.value, default=str, ensure_ascii=False)
        except Exception:
            val_text = str(m.value)
        cur.execute(
            "INSERT INTO measurements (source,node_id,name,category,value,unit,timestamp) VALUES (?,?,?,?,?,?,?)",
            (m.source, m.node_id, m.name, m.category, val_text, m.unit, m.timestamp),
        )
        self.conn.commit()

    def insert_alert(self, a: Alert):
        if not self.conn:
            raise RuntimeError("Database not initialized")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO alerts (name,node_id,severity,message,value,threshold,timestamp) VALUES (?,?,?,?,?,?,?)",
            (a.name, a.node_id, a.severity, a.message, a.value, a.threshold, a.timestamp),
        )
        self.conn.commit()

    def get_recent_measurements(self, limit: int = 100):
        if not self.conn:
            raise RuntimeError("Database not initialized")
        cur = self.conn.cursor()
        cur.execute(
            "SELECT source,node_id,name,category,value,unit,timestamp FROM measurements ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
