import json
from typing import Any, Optional, Tuple

from models.data_model import NormalizedData
from db.mysql_client import get_connection


def get_storable_values(val: Any) -> Tuple[Optional[float], Optional[str]]:
    """
    Sépare la valeur en deux parties stockables :
    - numeric_value : float ou None (pour la colonne value FLOAT)
    - text_value    : str ou None  (pour la colonne text_value TEXT)

    Règles :
    - int, float, bool → numeric_value
    - datetime-like, str, objets complexes → text_value
    - None → numeric_value = 0.0
    """
    if val is None:
        return 0.0, None

    if isinstance(val, bool):
        return 1.0 if val else 0.0, None

    if isinstance(val, (int, float)):
        return float(val), None

    # Tentative de conversion numérique
    try:
        return float(val), None
    except (TypeError, ValueError):
        pass

    # Tout le reste → texte (JSON si possible, sinon str)
    try:
        text = json.dumps(val, default=str, ensure_ascii=False)
        return None, text[:2000]  # limite raisonnable pour TEXT
    except Exception:
        return None, str(val)[:2000]


def process_data(data: NormalizedData) -> bool:
    """
    Enregistre une NormalizedData dans MySQL (tables nodes + measurements).
    Utilise deux colonnes : value (FLOAT) et text_value (TEXT).

    Retourne True si l'insertion a réussi, False sinon.
    """
    conn = None
    cursor = None
    success = False

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Vérifier / créer le node si nécessaire
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

        # 2. Préparer les deux valeurs stockables
        numeric_value, text_value = get_storable_values(data.value)

        print(f"  Valeur stockée pour {data.name}: "
              f"numeric={numeric_value!r} | text={text_value!r}")

        # 3. Insérer la mesure avec les deux colonnes
        cursor.execute(
            """
            INSERT INTO measurements 
            (node_id, value, text_value, timestamp)
            VALUES (%s, %s, %s, FROM_UNIXTIME(%s))
            """,
            (node_db_id, numeric_value, text_value, int(data.timestamp))
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