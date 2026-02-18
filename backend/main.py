import json
import os

from connectors.opcua_connector import OPCUAConnector
from models.data_model import NormalizedData   # assure-toi que c'est bien importé
from normalizer.opcua_normalizer import normalize_opcua_data
from intelligence.stats_engine import StatsEngine
from intelligence.anomaly_engine import detect_anomaly
from intelligence.rules_engine import evaluate_rules
from storage.db import Database
from storage.mysql_storage import process_data as mysql_process


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

        # Pour le test : on prend les 5 premiers
        node_ids = [n["nodeid"] for n in nodes[:5]]
        print(f"→ Surveillance des nodes : {node_ids}")

        gen = connector.read_realtime(node_ids, interval=2.0)

        stats_engine = StatsEngine()

        # Forçage MySQL pour debug (à remettre en commentaire ou via config plus tard)
        use_mysql = True
        print("Mode FORCÉ : utilisation de MySQL activée")

        db = None
        if not use_mysql:
            db = Database()
            db.init_db()
            print("→ SQLite activé comme fallback")

        for cycle in range(1, 4):  # 3 cycles de test
            print(f"\nCycle {cycle} ────────────────")
            raw_batch = next(gen)
            
            for item in raw_batch:
                node_id = item.get("nodeid")
                value = item.get("value")
                raw_name = item.get("name")

                normalized = normalize_opcua_data(node_id, value, raw_name=raw_name)
                print(f"  {normalized.name:<18} = {normalized.value!r}  ({type(normalized.value).__name__})")

                # Persistance
                if use_mysql:
                    mysql_process(normalized)
                else:
                    try:
                        db.insert_measure(normalized)
                        print(f"   → SQLite OK")
                    except Exception as e:
                        print(f"   → ÉCHEC SQLite : {type(e).__name__} → {e}")

                # Statistiques
                stats = stats_engine.update(normalized)
                if stats:
                    print(f"   stats → avg={stats['avg']:.3f}  min={stats['min']}  max={stats['max']}")

                # Anomalie
                if stats and detect_anomaly(normalized.value, stats):
                    print(f"   ⚠️  Anomalie détectée sur {normalized.name}")

                # Règles / alertes
                alerts = evaluate_rules(normalized)
                for alert in alerts:
                    print(f"   🚨 {alert.severity} — {alert.message}")
                    if db:  # seulement si SQLite actif
                        try:
                            db.insert_alert(alert)
                        except Exception:
                            pass

        gen.close()

    except Exception as e:
        print(f"Erreur globale dans la boucle : {type(e).__name__} → {e}")

    finally:
        connector.disconnect()
        if db:
            try:
                db.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()