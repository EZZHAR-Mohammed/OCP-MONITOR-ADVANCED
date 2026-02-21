# opc_monitor_universel.py
from opcua import Client, ua
import time
from datetime import datetime


# CONFIGURATION
SERVER_URL = "opc.tcp://Mohammed_EZZHAR.lan:53530/OPCUA/SimulationServer"
START_NODE_ID = "ns=0;i=84"  # Objects
REFRESH_INTERVAL = 5
MAX_DEPTH = 5


def connect_to_server(url):
    client = Client(url)
    try:
        print(f"Tentative de connexion à : {url}")
        client.connect()
        print("Connexion réussie !\n")
        return client
    except Exception as e:
        print(f"Échec connexion : {e}")
        return None


def discover_variable_nodes_recursive(node, max_depth=5, current_depth=0):
    if current_depth >= max_depth:
        return []

    candidates = []
    try:
        browse_result = node.get_children()
        for child in browse_result:
            try:
                if child.get_node_class() == ua.NodeClass.Variable:
                    candidates.append((child, current_depth + 1))
            except:
                pass

            candidates.extend(discover_variable_nodes_recursive(child, max_depth, current_depth + 1))
    except:
        pass

    return candidates


def read_node_data(node):
    """Lecture sécurisée - retourne None si impossible"""
    try:
        # Tentative de lecture de la valeur (point critique)
        value = node.read_value()  # Si ça plante → except
    except Exception:
        return None  # Ignore silencieusement

    try:
        node_id = str(node.nodeid)
        display_name = node.get_display_name().Text if node.get_display_name() else "Sans nom"

        timestamp = datetime.now()
        try:
            timestamp_attr = node.read_attribute(ua.AttributeIds.SourceTimestamp)
            if timestamp_attr.SourceTimestamp:
                timestamp = timestamp_attr.SourceTimestamp
        except:
            pass

        return {
            "NodeId": node_id,
            "DisplayName": display_name,
            "Value": value,
            "LastUpdate": timestamp.strftime("%H:%M:%S")
        }
    except:
        return None


def main():
    client = connect_to_server(SERVER_URL)
    if not client:
        return

    try:
        start_node = client.get_node(START_NODE_ID)
        print(f"Nœud de départ : {start_node.nodeid} ({start_node.get_display_name().Text})\n")

        print(f"Découverte des candidats Variables (profondeur max {MAX_DEPTH})...")
        candidates = discover_variable_nodes_recursive(start_node, max_depth=MAX_DEPTH)
        print(f"{len(candidates)} candidats trouvés.\n")

        if not candidates:
            print("Aucun candidat trouvé.")
            return

        print("Lecture en continu - seuls les nœuds lisibles sont affichés\n")
        print("-" * 100)
        print(f"{'NodeId':<35} {'DisplayName':<50} {'Value':<40} {'Last Update':<15}")
        print("-" * 100)

        while True:
            print(f"\nHeure actuelle : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 100)

            readable_count = 0
            for node, depth in candidates:
                data = read_node_data(node)
                if data is None:
                    continue

                readable_count += 1
                indent = "  " * depth
                value_str = str(data['Value'])
                print(f"{indent}{data['NodeId']:<35} {indent + data['DisplayName']:<50} {value_str:<40} {data['LastUpdate']:<15}")

            print(f"\n{readable_count} variables lisibles sur {len(candidates)} candidats")
            print("-" * 100)
            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print("\nArrêt par l'utilisateur (Ctrl+C)")
    
    except Exception as e:
        print(f"Erreur générale : {e}")
    
    finally:
        client.disconnect()
        print("Connexion fermée.")


if __name__ == "__main__":
    main()