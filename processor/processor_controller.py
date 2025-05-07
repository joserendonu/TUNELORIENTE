from config import DETECTIONS_QUEUE
from clients.redis_client import redis_client
from validators.validator_process import process_message


def process_detections(threshold: float = 0.5) -> None:
    """Procesa detecciones en la cola Redis."""
    
    # Leer todos los mensajes pendientes en la cola DETECTIONS_QUEUE
    while True:
        try:
            # Leer mensajes acumulados en la cola antes de procesar el bucle principal
            pending_messages = redis_client.lrange(DETECTIONS_QUEUE, 0, -1)
            redis_client.ltrim(DETECTIONS_QUEUE, len(pending_messages), -1)

            # Procesar mensajes pendientes
            for detections_json in pending_messages:
                print("Leyendo buffer: deteccion")
                process_message(detections_json, threshold)

            # Entrar al bucle principal (escuchando nuevos mensajes)
            while True:
                _, detections_json = redis_client.brpop(DETECTIONS_QUEUE)
                print("Nueva deteccion")
                process_message(detections_json, threshold)

        except Exception as e:
            print(f"Error inesperado: {e}")
