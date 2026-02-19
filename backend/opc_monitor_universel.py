# opc_monitor_universel.py
from opcua import Client, ua
import time
from datetime import datetime


# ───────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────
SERVER_URL = "opc.tcp://Mohammed_EZZHAR.lan:53530/OPCUA/SimulationServer"

# Nœud de départ (Objects = le plus utile)
START_NODE_ID = "ns=0;i=84"  # Objects

REFRESH_INTERVAL = 5  # secondes
MAX_DEPTH = 5         # limite profondeur
# ───────────────────────────────────────────────


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
    """Découvre récursivement SEULEMENT les nœuds qui sont Variables"""
    if current_depth >= max_depth:
        return []

    variables = []
    try:
        browse_result = node.get_children()
        for child in browse_result:
            try:
                # Test si c'est une Variable AVANT de l'ajouter
                if child.get_node_class() == ua.NodeClass.Variable:
                    variables.append((child, current_depth + 1))
            except:
                pass  # Ignore les nœuds où get_node_class() plante

            # Récursion sur tous les enfants
            variables.extend(discover_variable_nodes_recursive(child, max_depth, current_depth + 1))
    except Exception as e:
        print(f"Erreur découverte enfants de {node.nodeid} : {e}")

    return variables


def read_node_data(node):
    """Lit les infos (protégé contre les nœuds non lisibles)"""
    try:
        node_id = str(node.nodeid)
        display_name = node.get_display_name().Text if node.get_display_name() else "Sans nom"

        # Double vérification : on tente read_value seulement si c'est une Variable
        if node.get_node_class() == ua.NodeClass.Variable:
            value = node.read_value()
        else:
            value = "Non lisible (non Variable)"

        timestamp_attr = node.read_attribute(14)  # SourceTimestamp
        timestamp = timestamp_attr.SourceTimestamp if timestamp_attr.SourceTimestamp else datetime.now()
        return {
            "NodeId": node_id,
            "DisplayName": display_name,
            "Value": value,
            "LastUpdate": timestamp.strftime("%H:%M:%S")
        }
    except Exception as e:
        return {
            "NodeId": str(node.nodeid),
            "DisplayName": "Erreur",
            "Value": f"Erreur: {e}",
            "LastUpdate": datetime.now().strftime("%H:%M:%S")
        }


def main():
    client = connect_to_server(SERVER_URL)
    if not client:
        return

    try:
        start_node = client.get_node(START_NODE_ID)
        print(f"Nœud de départ : {start_node.nodeid} ({start_node.get_display_name().Text})\n")

        print(f"Découverte des Variables (profondeur max {MAX_DEPTH})...")
        variable_nodes = discover_variable_nodes_recursive(start_node, max_depth=MAX_DEPTH)
        print(f"{len(variable_nodes)} Variables trouvées.\n")

        if not variable_nodes:
            print("Aucune Variable trouvée. Essaye un autre nœud de départ.")
            return

        print("Lecture en continu des Variables (Ctrl+C pour arrêter)\n")
        print("-" * 100)
        print(f"{'NodeId':<35} {'DisplayName':<50} {'Value':<40} {'Last Update':<15}")
        print("-" * 100)

        while True:
            print(f"\nHeure actuelle : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 100)

            for node, depth in variable_nodes:
                data = read_node_data(node)
                indent = "  " * depth
                print(f"{indent}{data['NodeId']:<35} {indent + data['DisplayName']:<50} {str(data['Value']):<40} {data['LastUpdate']:<15}")

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