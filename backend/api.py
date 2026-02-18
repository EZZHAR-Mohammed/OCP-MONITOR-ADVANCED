from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error
from typing import List, Dict

app = FastAPI(
    title="OCP Monitor API",
    version="1.0",
    description="API pour consulter les données OPC UA collectées et stockées dans MySQL"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clients WebSocket
active_connections: List[WebSocket] = []

async def broadcast(message: dict):
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.append(connection)
    for conn in disconnected:
        active_connections.remove(conn)
    print(f"Broadcast envoyé à {len(active_connections)} clients : {message.get('type')}")

# ROUTE WEBSOCKET – OBLIGATOIRE
@app.websocket("/ws/measurements")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print("Nouveau client WebSocket connecté")
    try:
        latest = get_latest_measurements(50)
        print(f"Envoi initial : {len(latest)} mesures")
        await websocket.send_json({"type": "initial", "data": latest})

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("Client WebSocket déconnecté")
    except Exception as e:
        print(f"Erreur WebSocket : {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

# DB config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "opcua_monitor"
}

@contextmanager
def get_db():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        yield conn
    except Error as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API OCP Monitor !", "docs": "/docs"}

@app.get("/nodes", response_model=List[Dict])
def get_nodes():
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM nodes ORDER BY id")
        return cur.fetchall()

@app.get("/measurements/latest", response_model=List[Dict])
def get_latest_measurements(limit: int = 50):
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                n.name, n.node_id, n.category, n.unit,
                m.value AS numeric_value, m.text_value,
                m.timestamp, m.timestamp AS readable_time
            FROM measurements m
            JOIN nodes n ON m.node_id = n.id
            ORDER BY m.timestamp DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        for row in rows:
            row['timestamp'] = str(row['timestamp'])
            row['readable_time'] = str(row['readable_time'])
        return rows

@app.get("/measurements/{node_id}", response_model=List[Dict])
def get_measurements_by_node(node_id: int, limit: int = 100):
    with get_db() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                m.id, n.name, n.node_id, n.category, n.unit,
                m.value AS numeric_value, m.text_value,
                m.timestamp, m.timestamp AS readable_time
            FROM measurements m
            JOIN nodes n ON m.node_id = n.id
            WHERE m.node_id = %s
            ORDER BY m.timestamp DESC
            LIMIT %s
        """, (node_id, limit))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No measurements found")
        for row in rows:
            row['timestamp'] = str(row['timestamp'])
            row['readable_time'] = str(row['readable_time'])
        return rows