import asyncio
import threading

from api import broadcast

# Boucle asyncio dédiée
loop = asyncio.new_event_loop()
notifier_thread = None

def start_notifier_loop():
    global notifier_thread
    if notifier_thread and notifier_thread.is_alive():
        return
    notifier_thread = threading.Thread(target=loop.run_forever, daemon=True)
    notifier_thread.start()
    print("Notifier WebSocket démarré dans un thread séparé")

def notify_new_measurement(payload: dict):
    if not notifier_thread or not notifier_thread.is_alive():
        start_notifier_loop()
    asyncio.run_coroutine_threadsafe(broadcast(payload), loop)
    print(f"Notification envoyée : {payload['type']}")