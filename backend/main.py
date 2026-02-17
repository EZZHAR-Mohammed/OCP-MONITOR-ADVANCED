import json
import os

from connectors.opcua_connector import OPCUAConnector
from models.data_model import SensorData
from normalizer.opcua_normalizer import normalize_opcua_data
from intelligence.stats_engine import StatsEngine
from intelligence.anomaly_engine import detect_anomaly
from intelligence.rules_engine import evaluate_rules
from storage.db import Database


def load_config(path: str = "config/opcua_config.json") -> dict:
    cfg_path = os.path.join(os.path.dirname(__file__), path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    cfg = load_config()
    endpoint = cfg.get("endpoint")
    username = cfg.get("username")
    password = cfg.get("password")

    connector = OPCUAConnector(endpoint, username=username, password=password)
    connector.connect()
    try:
        root = connector.get_root()
        nodes = connector.browse_nodes(root, max_level=3)
        print(f"Found {len(nodes)} nodes (sample):")
        for n in nodes[:20]:
            print(n)

        # choose a small set of VARIABLE node ids to read
        node_ids = [n["nodeid"] for n in nodes[:5]]
        gen = connector.read_realtime(node_ids, interval=2)
        stats_engine = StatsEngine()
        db = Database()
        db.init_db()
        for _ in range(3):
            raw_batch = next(gen)
            normalized_batch = []
            for item in raw_batch:
                # item expected: {"name", "nodeid", "value", "timestamp"}
                node_id = item.get("nodeid")
                value = item.get("value")
                raw_name = item.get("name")
                normalized = normalize_opcua_data(node_id, value, raw_name=raw_name)
                normalized_batch.append(normalized)
                print(normalized)

                # Persist measurement
                try:
                    db.insert_measure(normalized)
                except Exception:
                    pass

                # Stats
                stats = stats_engine.update(normalized)
                if stats:
                    print(f"stats {normalized.name}: avg={stats['avg']:.3f} min={stats['min']} max={stats['max']}")

                # Anomaly detection
                if stats and detect_anomaly(normalized.value, stats):
                    print(f"⚠️ Anomalie détectée sur {normalized.name}")

                # Rules / alerts
                alerts = evaluate_rules(normalized)
                for alert in alerts:
                    print(f"🚨 {alert.severity} — {alert.message} (value={alert.value} thr={alert.threshold})")
                    try:
                        db.insert_alert(alert)
                    except Exception:
                        pass
        try:
            gen.close()
        except Exception:
            pass
    finally:
        connector.disconnect()
        try:
            db.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
