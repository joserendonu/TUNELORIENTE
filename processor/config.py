import os
from pathlib import Path

REDIS_HOST = os.getenv("REDIS_HOST", "redis-server")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
WEBSOCKET_SERVER = os.getenv("WEBSOCKET_SERVER", "ws://host.docker.internal:8765")
DETECTIONS_QUEUE = os.getenv("DETECTIONS_QUEUE", "detections_queue")
BUFFER_QUEUE = os.getenv("BUFFER_QUEUE", "buffer_ws")
BASE_DIR = Path(__file__).parent