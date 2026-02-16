from opcua import Client
from opcua.ua import NodeClass
import time
from typing import List, Dict


class OPCUAConnector:
    """Generic OPC UA connector using FreeOpcUa (package name: opcua).

    Features:
    - connect / disconnect
    - browse nodes recursively (limited depth)
    - read single node value
    - realtime generator reading a list of node ids
    """

    def __init__(self, endpoint: str, username: str = None, password: str = None, security: str = "None"):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.security = security
        self.client = Client(endpoint)
        if username and password:
            self.client.set_user(username)
            self.client.set_password(password)

    def connect(self, timeout: int = 10):
        """Connect to the OPC UA server."""
        self.client.connect()
        print("✅ Connecté au serveur OPC UA")

    def disconnect(self):
        """Disconnect (safe)."""
        try:
            self.client.disconnect()
        except Exception:
            pass
        print("🔌 Déconnecté")

    def get_root(self):
        """Return the root node object."""
        return self.client.get_root_node()

    def browse_nodes(self, node, level: int = 0, max_level: int = 3) -> List[Dict]:
        """Recursively browse children up to max_level and return a list of VARIABLE node info dicts.

        Each dict contains: nodeid, name, level
        Only nodes with NodeClass.Variable are returned to avoid system nodes.
        """
        nodes = []
        if level > max_level:
            return nodes

        try:
            children = node.get_children()
        except Exception:
            return nodes

        for child in children:
            try:
                node_class = child.get_node_class()
                # Keep only Variables (sensors / data nodes)
                if node_class == NodeClass.Variable:
                    browse_name = child.get_browse_name()
                    name = getattr(browse_name, "Name", str(child.nodeid))
                    node_info = {
                        "nodeid": child.nodeid.to_string(),
                        "name": name,
                        "level": level,
                    }
                    nodes.append(node_info)

                # Always continue browsing children to find variables deeper in the tree
                nodes.extend(self.browse_nodes(child, level + 1, max_level))
            except Exception:
                # ignore errors for individual children to be robust to server quirks
                continue

        return nodes

    def read_value(self, node_id: str):
        """Read a single node and return a dict with readable name and value.

        Returns None on error or if the value is None.
        node_id should be the string form returned by node.nodeid.to_string().
        """
        try:
            node = self.client.get_node(node_id)
            value = node.get_value()
            if value is None:
                return None
            browse_name = node.get_browse_name()
            name = getattr(browse_name, "Name", str(node.nodeid))
            return {"name": name, "nodeid": node.nodeid.to_string(), "value": value}
        except Exception:
            return None

    def read_realtime(self, node_ids: List[str], interval: float = 1.0):
        """Generator yielding list of dicts with name, nodeid, value, timestamp every `interval` seconds.

        Skips nodes whose value is None or which cannot be read.
        """
        try:
            while True:
                data = []
                for nid in node_ids:
                    item = self.read_value(nid)
                    if not item:
                        continue
                    item["timestamp"] = time.time()
                    data.append(item)
                yield data
                time.sleep(interval)
        except GeneratorExit:
            return
        except Exception:
            return
