from fastapi import FastAPI, HTTPException
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error
from typing import List, Dict

app = FastAPI(
    title="OCP Monitor API",
    version="1.0",
    description="API pour consulter les données OPC UA collectées et stockées dans MySQL"
)

# Configuration de la base de données
# À terme : déplacer ces valeurs dans un fichier .env + python-dotenv
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",                 # mets ton mot de passe si tu en as un
    "database": "opcua_monitor"     # vérifie que c'est bien le nom exact
}

@contextmanager
def get_db():
    """Gestionnaire de contexte pour la connexion MySQL"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de connexion à la base : {str(e)}")
    finally:
        if conn and conn.is_connected():
            conn.close()


# ────────────────────────────────────────────────
# Route racine (accueil de l'API)
# ────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur l'API OCP Monitor !",
        "docs": "Va sur /docs pour voir la documentation interactive (Swagger)",
        "endpoints": [
            "/nodes → Liste des nœuds OPC UA surveillés",
            "/measurements/latest → Dernières mesures (tous nœuds)",
            "/measurements/{node_id} → Historique des mesures pour un nœud spécifique"
        ],
        "status": "API opérationnelle"
    }


# ────────────────────────────────────────────────
# Liste de tous les nœuds
# ────────────────────────────────────────────────
@app.get("/nodes", response_model=List[Dict])
def get_nodes():
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM nodes ORDER BY id")
        return cur.fetchall()


# ────────────────────────────────────────────────
# Dernières mesures (tous nœuds)
# ────────────────────────────────────────────────
@app.get("/measurements/latest", response_model=List[Dict])
def get_latest_measurements(limit: int = 50):
    """
    Retourne les N dernières mesures (par défaut 50),
    triées par timestamp descendant, avec le nom du nœud,
    les valeurs numériques ET textuelles.
    """
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                n.name, 
                n.node_id, 
                n.category, 
                n.unit,
                m.value          AS numeric_value,
                m.text_value     AS text_value,
                m.timestamp,
                m.timestamp      AS readable_time
            FROM measurements m
            JOIN nodes n ON m.node_id = n.id
            ORDER BY m.timestamp DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()


# ────────────────────────────────────────────────
# Historique d'un nœud spécifique
# ────────────────────────────────────────────────
@app.get("/measurements/{node_id}", response_model=List[Dict])
def get_measurements_by_node(node_id: int, limit: int = 100):
    """
    Retourne l'historique des mesures pour un node_id donné
    (limité à N enregistrements, par défaut 100)
    """
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                m.id,
                n.name,
                n.node_id,
                n.category,
                n.unit,
                m.value          AS numeric_value,
                m.text_value     AS text_value,
                m.timestamp,
                m.timestamp      AS readable_time
            FROM measurements m
            JOIN nodes n ON m.node_id = n.id
            WHERE m.node_id = %s
            ORDER BY m.timestamp DESC
            LIMIT %s
        """, (node_id, limit))
        
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune mesure trouvée pour le node_id {node_id}"
            )
        return rows