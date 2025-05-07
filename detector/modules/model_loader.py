from ultralytics import YOLO
from ultralytics.engine.results import Results

import torch
import numpy as np
from typing import List


class ModelLoader:
    """Clase para cargar y manejar el modelo de detección YOLO.
    
    attributes:
        model (YOLO): Modelo YOLOv8.
        image_size (int): Tamaño de la imagen de entrada.
        confidence (float): Umbral de confianza para detección.
        class_filter (List[int]): Lista de IDs de clases a filtrar.
        class_names (List[str]): Nombres de las clases del modelo.
    """
    def __init__(
        self,
        weights_path: str,
        image_size: int = 640,
        confidence: float = 0.5,
        class_filter: List[int] = None
    ) -> None:
        self.model = YOLO(weights_path)
        self.image_size = image_size
        self.confidence = confidence
        self.class_filter = class_filter
        self.class_names = self.model.names


    def detect(self, image: np.array) -> Results:
        """Realiza la detección de objetos en una imagen.
        args:
            image (np.array): Imagen de entrada.
        returns:
            Results: Resultados de la detección.
        """

        ultralytics_results = self.model(
            source=image,
            imgsz=self.image_size,
            conf=self.confidence,
            classes=self.class_filter,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            agnostic_nms=True,
            verbose=False
        )[0]
        
        return ultralytics_results
    

    def track(self, image: np.array) -> Results:
        """Realiza el seguimiento de objetos en una imagen.
        args:
            image (np.array): Imagen de entrada.
        returns:
            Results: Resultados del seguimiento.
        """
        
        ultralytics_results = self.model.track(
            source=image,
            persist=True,
            imgsz=self.image_size,
            conf=self.confidence,
            classes=self.class_filter,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            agnostic_nms=True,
            verbose=False,
            tracker="bytetrack.yaml"
        )[0]
        
        return ultralytics_results
    