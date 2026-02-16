import json
import os

from connectors.opcua_connector import OPCUAConnector
from models.data_model import SensorData


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

        # choose a small set of node ids to read
        node_ids = [n["nodeid"] for n in nodes[:5]]
        gen = connector.read_realtime(node_ids, interval=2)
        for _ in range(3):
            batch = next(gen)
            for item in batch:
                sd = SensorData(item.get("nodeid"), item.get("value"), item.get("timestamp"))
                print(sd.to_dict())
        try:
            gen.close()
        except Exception:
            pass
    finally:
        connector.disconnect()


if __name__ == "__main__":
    main()
