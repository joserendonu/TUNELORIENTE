import supervision as sv
import redis

import json
import cv2
import base64
import numpy as np
import pandas as pd

from config import DETECTIONS_QUEUE, redis_client, get_current_timestamp
from camera_controller import load_camera_config

from tools.video_info import VideoInfo


class SaveResults:
    """Clase para enviar resultados de detección a Redis.

    attributes:
        camera_id (str): ID de la cámara.
        timestamp (str): Timestamp de la detección.
        camera_config (dict): Información de la cámara.
    
    callback:
        send_detection (function): Función para enviar resultados.
    """
    def __init__(
        self,
        camera_id: str,
        timestamp: str = get_current_timestamp().strftime("%Y%m%d%H%M%S"),
    ) -> None:
        self.camera_id = camera_id
        self.timestamp = timestamp

        self.camera_config = load_camera_config(camera_id)


    def codificar_imagen(self, image: np.array) -> str:
        """Codifica la imagen en formato base64.

        args:
            image (np.array): Imagen original.
        """
        # Reducir tamaño de la imagen
        h, w = image.shape[:2]
        image_rgb = cv2.resize(image, (w//2, h//2), interpolation=cv2.INTER_AREA)

        # Codificar imagen en base64
        success, encoded_image = cv2.imencode(".jpg", image_rgb)
        if not success:
            return "Error al codificar la imagen."

        image_bytes = encoded_image.tobytes()
        img_base64 = base64.b64encode(image_bytes).decode('ascii')

        return img_base64


    def convertir_json(self, detection, img_base64: str):
        """Convierte los resultados de detección a formato JSON.

        args:
            detection (sv.Detections): Resultados de detección.
            img_base64 (str): Imagen codificada en base64.
        """
        if len(detection) > 5 and detection[4] is not None and isinstance(detection[5], dict) and 'class_name' in detection[5]:
            self.new_id = f"{self.timestamp}{detection[4]}"

            detections_json = {
                "nombre_camara": self.camera_config['nombre'],
                "id": self.new_id,
                "confianza": float(detection[2]),
                "clase": detection[5]['class_name'],
                "tiempo": get_current_timestamp().strftime("%Y_%m_%d_%H_%M_%S.%f"),
                "imagen": img_base64
            }

            return json.dumps(detections_json)
        else:                                                                                                             
            return None


    def send_detection(self, detections: sv.Detections, image: np.array) -> None:
        """Envía los resultados de detección a Redis.

        args:
            detections (sv.Detections): Resultados de detección.
            image (np.array): Imagen original.
        """

        for detection in detections:
            img_base64 = self.codificar_imagen(image)
            detection_json_str = self.convertir_json(detection, img_base64)

            print(detection_json_str)
            quit()

            try:
                redis_client.lpush(DETECTIONS_QUEUE, detection_json_str)
                print(f"[{self.camera_id} - {self.camera_config['nombre']}] Detección enviada: {self.timestamp}{detection[4]}")
            except redis.ConnectionError as e:
                print(f"Error al conectarse a Redis: {e}")
            finally:
                redis_client.close()
