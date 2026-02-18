import json
from typing import Optional
from models.data_model import NormalizedData
from db.mysql_client import get_connection


def save_node(data: NormalizedData):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT IGNORE INTO nodes (node_id, name, category, unit)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (data.node_id, data.name or '', data.category or '', data.unit or ''))
    conn.commit()
    cursor.close()
    conn.close()


def save_measurement(node_db_id: int, value, timestamp: int):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO measurements (node_id, value, timestamp)
    VALUES (%s, %s, FROM_UNIXTIME(%s))
    """
    cursor.execute(query, (node_db_id, float(value), int(timestamp)))
    conn.commit()
    cursor.close()
    conn.close()


def process_data(data: NormalizedData):
    """Persist a NormalizedData instance into nodes + measurements tables.

    If the node does not exist it will be inserted (id retrieved after).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM nodes WHERE node_id = %s", (data.node_id,))
    node = cursor.fetchone()

    if not node:
        # insert minimal node metadata
        cursor.execute(
            "INSERT INTO nodes (node_id, name, category, unit) VALUES (%s, %s, %s, %s)",
            (data.node_id, data.name or '', data.category or '', data.unit or ''),
        )
        conn.commit()
        cursor.execute("SELECT id FROM nodes WHERE node_id = %s", (data.node_id,))
        node = cursor.fetchone()

    if node:
        node_id = node["id"] if isinstance(node, dict) else node[0]
        # try convert value to float when possible, otherwise store as JSON string
        try:
            v = float(data.value)
        except Exception:
            try:
                v = json.dumps(data.value, default=str, ensure_ascii=False)
            except Exception:
                v = str(data.value)

        cursor.execute(
            "INSERT INTO measurements (node_id, value, timestamp) VALUES (%s, %s, FROM_UNIXTIME(%s))",
            (node_id, v, int(data.timestamp)),
        )
        conn.commit()

    cursor.close()
    conn.close()
