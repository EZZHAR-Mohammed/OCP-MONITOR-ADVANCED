import json
import os
import time
from threading import Thread

from connectors.opcua_connector import OPCUAConnector
from models.data_model import NormalizedData
from normalizer.opcua_normalizer import normalize_opcua_data
from intelligence.stats_engine import StatsEngine
from intelligence.anomaly_engine import detect_anomaly
from intelligence.rules_engine import evaluate_rules
from storage.db import Database
from storage.mysql_storage import process_data as mysql_process

# Démarrage du notifier WebSocket
from ws_notifier import start_notifier_loop
start_notifier_loop()

def load_config(path: str = "config/opcua_config.json") -> dict:
    cfg_path = os.path.join(os.path.dirname(__file__), path)
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erreur : fichier de config {cfg_path} introuvable")
        return {}
    except json.JSONDecodeError:
        print("Erreur : format JSON invalide dans la config")
        return {}


def main():
    cfg = load_config()
    endpoint = cfg.get("endpoint")
    if not endpoint:
        print("ERREUR : endpoint OPC UA non défini dans la config")
        return

    username = cfg.get("username")
    password = cfg.get("password")

    print(f"Connexion OPC UA → {endpoint}")
    connector = OPCUAConnector(endpoint, username=username, password=password)
    connector.connect()

    try:
        root = connector.get_root()
        nodes = connector.browse_nodes(root, max_level=3)
        print(f"→ {len(nodes)} nœuds variables trouvés")

        # On prend les 5 premiers nœuds (tu peux augmenter si tu veux)
        node_ids = [n["nodeid"] for n in nodes[:5]]
        print(f"→ Surveillance des nodes : {node_ids}")

        gen = connector.read_realtime(node_ids, interval=1.0)  # ← 1 seconde

        stats_engine = StatsEngine()

        use_mysql = True
        print("Mode FORCÉ : utilisation de MySQL activée")

        db = None
        if not use_mysql:
            db = Database()
            db.init_db()
            print("→ SQLite activé comme fallback")

        print("=== COLLECTE EN TEMPS RÉEL DÉMARRÉE (toutes les 1 seconde) ===")

        # Boucle infinie
        while True:
            raw_batch = next(gen)
            
            for item in raw_batch:
                node_id = item.get("nodeid")
                value = item.get("value")
                raw_name = item.get("name")

                normalized = normalize_opcua_data(node_id, value, raw_name=raw_name)

                # Persistance
                if use_mysql:
                    mysql_process(normalized)
                else:
                    try:
                        db.insert_measure(normalized)
                    except Exception as e:
                        print(f"   → ÉCHEC SQLite : {type(e).__name__} → {e}")

                # Stats, anomalies, alertes (optionnel)
                stats = stats_engine.update(normalized)
                if stats:
                    print(f"   stats → avg={stats['avg']:.3f}  min={stats['min']}  max={stats['max']}")

                if stats and detect_anomaly(normalized.value, stats):
                    print(f"   ⚠️  Anomalie détectée sur {normalized.name}")

                alerts = evaluate_rules(normalized)
                for alert in alerts:
                    print(f"   🚨 {alert.severity} — {alert.message}")

            # Petite pause pour éviter surcharge CPU (facultatif)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nArrêt manuel par l'utilisateur...")
    except Exception as e:
        print(f"Erreur globale : {type(e).__name__} → {e}")
    finally:
        connector.disconnect()
        if db:
            try:
                db.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()