import json
from typing import Any, Union

from models.data_model import NormalizedData
from db.mysql_client import get_connection


def get_storable_value(val: Any) -> Union[float, int, str]:
    """
    Transforme la valeur en un format stockable dans MySQL :
    - numériques → float ou int
    - le reste → chaîne JSON ou str (limité en longueur)
    """
    if isinstance(val, (int, float)):
        return float(val)          # on uniformise en float pour la colonne
    if isinstance(val, bool):
        return 1.0 if val else 0.0
    if val is None:
        return 0.0

    try:
        return float(val)
    except (TypeError, ValueError):
        pass

    # Fallback texte
    try:
        text = json.dumps(val, default=str, ensure_ascii=False)
        return text[:1000]  # sécurité contre valeurs trop longues
    except Exception:
        return str(val)[:1000]


def process_data(data: NormalizedData) -> bool:
    """
    Enregistre NormalizedData dans MySQL (tables nodes + measurements).
    Retourne True si l'insertion a réussi, False sinon.
    """
    conn = None
    cursor = None
    success = False

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Vérifier / créer le node
        cursor.execute(
            "SELECT id FROM nodes WHERE node_id = %s LIMIT 1",
            (data.node_id,)
        )
        node_row = cursor.fetchone()

        if not node_row:
            cursor.execute(
                """
                INSERT INTO nodes (node_id, name, category, unit)
                VALUES (%s, %s, %s, %s)
                """,
                (data.node_id, data.name or '', data.category or '', data.unit or '')
            )
            conn.commit()
            cursor.execute(
                "SELECT id FROM nodes WHERE node_id = %s LIMIT 1",
                (data.node_id,)
            )
            node_row = cursor.fetchone()

        if not node_row:
            print(f"ERREUR : impossible de récupérer/créer le node {data.node_id}")
            return False

        node_db_id = node_row['id']

        # 2. Préparer la valeur stockable
        v = get_storable_value(data.value)
        print(f"  Valeur stockée pour {data.name}: {type(v).__name__} → {v!r}")

        # 3. Insérer la mesure
        cursor.execute(
            """
            INSERT INTO measurements (node_id, value, timestamp)
            VALUES (%s, %s, FROM_UNIXTIME(%s))
            """,
            (node_db_id, v, int(data.timestamp))
        )
        conn.commit()
        success = True
        print(f"   → MySQL OK : {data.name} enregistré")

    except Exception as e:
        print(f"   → ÉCHEC MySQL {data.name} : {type(e).__name__} → {e}")
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return success