from websockets.sync.client import connect
from config import WEBSOCKET_SERVER, BUFFER_QUEUE
from clients.redis_client import redis_client


def send_to_alert_device(message: str, path:str="detections"):
    try:
        with connect(f"{WEBSOCKET_SERVER}/{path}") as websocket:
            websocket.send(message)
            response = websocket.recv()
    except Exception as e:
        print(f"WebSocket caído. Guardando en buffer")
        redis_client.lpush(BUFFER_QUEUE, message)
