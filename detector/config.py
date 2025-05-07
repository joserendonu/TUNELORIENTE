import os
import redis
from pathlib import Path
import datetime
import pytz
TZ = pytz.timezone("America/Bogota") 

REDIS_SERVER= os.getenv("REDIS_SERVER", "redis-server")
DETECTIONS_QUEUE = os.getenv("DETECTIONS_QUEUE", "detections_queue")
BASE_DIR = Path(__file__).parent

redis_client = redis.Redis(host=REDIS_SERVER, port=6379, db=0)

def get_current_timestamp():
    """Retorna el timestamp con la zona horaria configurada."""
    now = datetime.datetime.now(pytz.utc).astimezone(TZ)
    return now
