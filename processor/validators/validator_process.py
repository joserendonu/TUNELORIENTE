import json
import pandas as pd
from pathlib import Path
from config import BUFFER_QUEUE
from clients.redis_client import redis_client
from clients.websocket_client import send_to_alert_device


def process_message(detections_json, threshold):
    """Procesa un mensaje individual."""
    try:
        # Convertir JSON a dict
        detections_data = json.loads(detections_json)

        # Convertir a lista si es un único objeto
        if isinstance(detections_data, dict):
            detections_data = [detections_data]

        # Crear DataFrame desde lista
        detections_df = pd.DataFrame(detections_data)

        # Procesar cada detección
        for _, detection in detections_df.iterrows():
            if detection['confianza'] > threshold:
                detection_id = detection['id']

                # Guardar detección en archivo si no existe
                if not Path(f"{detection_id}.json").exists():
                    with open(f"{detection_id}.json", 'w') as f:
                        f.write(detection.to_json())
                    send_to_alert_device(detection.to_json())

        # Procesar mensajes acumulados en BUFFER_QUEUE
        buffered_messages = redis_client.lrange(BUFFER_QUEUE, 0, -1)  # Leer todos los mensajes en la cola
        redis_client.ltrim(BUFFER_QUEUE, len(buffered_messages), -1)  # Limpiar los mensajes procesados

        for buffered_msg in buffered_messages:
            if buffered_msg:  # Validar que el mensaje no esté vacío
                send_to_alert_device(buffered_msg.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
    except Exception as e:
        print(f"Error inesperado al procesar mensaje: {e}")
