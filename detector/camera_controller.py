
import json
import os


def load_camera_config(camera_id: str) -> dict:
    """Carga la configuración de la cámara desde camera_config.json.
    
    args:
        camera_id (str): El ID de la cámara para la que se desea cargar la configuración.
    returns:
        dict: La configuración de la cámara.
    """

    # Verificar si el archivo de configuración existe
    if not os.path.exists("camera_config.json"):
        raise FileNotFoundError("El archivo de configuración camera_config.json no se encuentra.")
    
    # Cargar la configuración desde el archivo JSON
    with open("camera_config.json", "r") as f:
        config = json.load(f)
    
    # Verificar si la cámara está en la configuración
    if camera_id not in config:
        raise ValueError(f"Configuración no encontrada para {camera_id}")

    return config[camera_id]
