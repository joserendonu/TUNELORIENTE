import argparse
from camera_controller import load_camera_config
import detector_controller
from config import BASE_DIR


def main(camara_id: str) -> None:
    """Función principal para iniciar el 
    
    args:
        camara_id (str): ID de la cámara.
    """
    # Cargar la configuración de la cámara
    camera_config = load_camera_config(camara_id)

    # Inicializar el controlador de detección
    detector_controller.main(
    source=camera_config["url"],
    camera_id=camara_id,
    classes=camera_config["clases"],
    weights=BASE_DIR.joinpath(camera_config.get("weights",'weights/tunel_yolo11n.pt')).resolve(),
    size=int(camera_config.get("size", 1280)),
    confidence=float(camera_config.get("confidence", 0.5)),
    clip=int(camera_config.get("clip", 0)),
    region=camera_config.get("region", None),)


if __name__ == "__main__":
    # Inicializar argumentos de entrada
    parser = argparse.ArgumentParser()
    parser.add_argument('--camara-id', type=str, required=True, help='id de la cámara')
    option = parser.parse_args()
    main(camara_id=option.camara_id)
