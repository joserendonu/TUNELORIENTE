import os
from pathlib import Path
 
WS_HOST = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("WS_PORT", 8765))
DELETE_DAYS = int(os.getenv("DELETE_DAYS", 30))
ERASE_HOUR= int(os.getenv("ERASE_HOUR", 12))
ERASE_MINUTE = int(os.getenv("ERASE_MINUTE", 00))
ERASE_SECOND = int(os.getenv("ERASE_MINUTE", 00))
ERASE_MSECOND = int(os.getenv("ERASE_MINUTE", 00))
ALARM_TIME = int(os.getenv("ALARM_TIME", 1000*60*5))
desktop_path = str((Path.home() / "Documents").resolve())
PATH_STORAGE = os.getenv("PATH_STORAGE", f"{desktop_path}\\detections")
PATH_LOGS = os.getenv("PATH_LOGS", f"{desktop_path}\\logs")
BASE_DIR = Path(__file__).parent
MEDIA_PATH = BASE_DIR.joinpath("media")


CLASSES = {
    
    "bicycle": {"sound":"Sonido1.wav", "name":"bicicleta"},
    "motorcycle": {"sound":"Sonido2.wav", "name":"motocicleta"},
    "person": {"sound":"Sonido3.wav", "name":"peaton"},
    "signal": {"sound":"Sonido4.wav", "name":"sustancia peligrosa"},
    "truck": {"sound":"Sonido5.wav", "name":"camión"}
    
}