import supervision as sv
import cv2
import torch
import argparse
import gc
import itertools
import numpy as np
from pathlib import Path

from imutils.video import FileVideoStream, WebcamVideoStream
from modules.model_loader import ModelLoader
from modules.annotation import Annotation
from modules.save_results import SaveResults
import tools.messages as messages
from tools.video_info import VideoInfo
from typing import List
from config import get_current_timestamp


def main(
    source: str,
    camera_id: str,
    classes: List[int],
    weights: str,
    size: int,
    confidence: float,
    clip: int,
    region: str,
    show: bool = False
) -> None:
    """Función principal para iniciar el procesamiento.
    
    args:
        source (str): URL de la cámara o archivo de video.
        camera_id (str): ID de la cámara.
        weights (str): Ruta al modelo de detección.
        classes (List[int]): Lista de clases a filtrar.
        size (int): Tamaño de entrada de la imagen para el modelo de detección.
        confidence (float): Umbral de confianza para la detección.
        clip (int, optional): Duración del clip de salida en segundos. Por defecto es 0.
        region (str, optional): Región de interés en formato JSON. Por defecto es None.
    """
    # Inicializar contador de etapas del proceso de detección y seguimientos
    step_count = itertools.count(1)
    
    # Inicializar captura de video
    source_info = VideoInfo(source=source)
    messages.step_message(next(step_count), 'Origen del Video Inicializado ✅')
    messages.source_message(source_info)

    # Inicializar guardado de resultados
    saving_results = SaveResults(
        camera_id=camera_id )
    messages.step_message(next(step_count), 'Guardado Configurado ✅')
    
    # Revisar disponibilidad de GPU
    messages.step_message(next(step_count), f"Procesador: {'GPU ✅' if torch.cuda.is_available() else 'CPU ⚠️'}")

    # Inicializar modelo YOLO
    yolo_tracker = ModelLoader(
        weights_path=weights,
        image_size=size,
        confidence=confidence,
        class_filter=classes )

    messages.step_message(next(step_count), f"Modelo {Path(weights).stem.upper()} Inicializado ✅")

    # Anotadores
    annotator = Annotation(
        source_info=source_info,
        fps=False,
        trace=True )

    # Inicio del thread de proceso de captura de frames de video
    if source_info.source_type == 'stream':
        video_stream = WebcamVideoStream(src=eval(source) if source.isnumeric() else source)
    elif source_info.source_type == 'file':
        video_stream = FileVideoStream(source)

    # Inicializar variables
    frame_number = 0
    video_stream.stream.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    fps_monitor = sv.FPSMonitor()

    # Iniciar procesamiento de video
    messages.step_message(next(step_count), 'Procesamiento de Video Iniciado ✅')
    time_start = get_current_timestamp()
    video_stream.start()

    try:
        while video_stream.more() if source_info.source_type == 'file' else True:
            fps_monitor.tick()
            fps_value = fps_monitor.fps
            
            image = video_stream.read()
            if image is None:
                # gc.collect()
                print("Reconexión fallida tras varios intentos. Finalizando...")
                continue
            annotated_image = image.copy()

            if region:
                # Extraer región de interés 
                mask = np.zeros_like(annotated_image[:, :, 0])
                mask = cv2.fillPoly(mask, [np.array(region)], 255)
                masked_frame = cv2.bitwise_and(annotated_image, annotated_image, mask=mask)

                # Inferencia sobre la región de interés
                results = yolo_tracker.track(image=masked_frame)
                del masked_frame
            else:
                # Inferencia sobre toda la imagen
                results = yolo_tracker.track(image=image)

            # Conversión deresultados a formato Supervision
            detections = sv.Detections.from_ultralytics(ultralytics_results=results)
    
            # Dibujar anotaciones
            annotated_image = annotator.on_detections(detections=detections, scene=image)
            if detections:
                # Enviar detecciones
                saving_results.send_detection(detections=detections, image=annotated_image)

            # Presentar progreso en la terminal
            messages.progress_message(frame_number, source_info.total_frames, fps_value)
            
            frame_number += 1

            # Mostrar resultados en vivo
            if show:
                cv2.namedWindow('Resultado', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Resultado', 1280, 720)
                cv2.imshow("Resultado", annotated_image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("Saliendo...")
                    break

            # Liberar variables
            del image, annotated_image, results
            gc.collect()

    except KeyboardInterrupt:
        messages.step_message(next(step_count), 'Fin del video ✅')

    # Finalizar y mostrar tiempo total
    messages.step_message(next(step_count), f"Tiempo Total: {(get_current_timestamp() - time_start).total_seconds():.2f} s")
    video_stream.stop()
    if show:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Inicializar argumentos de entrada
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, required=True, help='source url')
    parser.add_argument('--camera-id', type=str, required=True, help='camera id')
    parser.add_argument('--weights', type=str, default='yolo11m.pt', help='model name')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class id: --classes 0, or --classes 0 2 3')
    parser.add_argument('--size', type=int, default=640, help='inference size in pixels')
    parser.add_argument('--confidence', type=float, default=0.5, help='inference confidence threshold')
    parser.add_argument('--clip', type=int, default=0, help='duration of output video clips in seconds')
    parser.add_argument('--region', type=str, default="0", help='region of interest')

    option = parser.parse_args()

    # Carpeta raíz del proyecto
    root_path = Path(__file__).resolve().parent

    main(
        source=option.source,
        camera_id=option.camera_id,
        weights=f"{root_path}/weights/{option.weights}",
        classes=option.classes,
        size=option.size,
        confidence=option.confidence,
        clip=option.clip,
        region=option.region
    )
