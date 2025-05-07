import json
from datetime import datetime, timedelta
import os
import csv
import shutil
from PIL import Image, ImageTk, UnidentifiedImageError
from io import BytesIO
import base64
import io
from config import (
    ERASE_HOUR,
    ERASE_MINUTE,
    ERASE_MSECOND,
    ERASE_SECOND,
    PATH_LOGS,
    PATH_STORAGE,
    PATH_LOGS,
)
import asyncio
from websockets.server import serve
import sys
import datetime as dt

from config import CLASSES


def detection_report(
    id_detection,
    id_camera,
    frame_detection,
    confidence,
    detection_class,
    time_detection,
):
    """
    Maneja los mensajes recibidos por WebSocket, decodifica los datos de detección en formato JSON,
    y registra los datos en un archivo CSV.

    Args:
        websocket: Conexión WebSocket desde la cual se reciben los datos de detección.
    """

    # Obtener fecha actual y construir carpeta para los csv y las imágenes
    fecha = datetime.now().strftime("%Y-%m-%d")
    carpeta = os.path.expanduser(
        f"" + PATH_STORAGE + "/" + str(id_camera) + "/" + str(fecha)
    )
    imgcarpeta = os.path.expanduser(
        f"" + PATH_STORAGE + "/" + str(id_camera) + "/" + str(fecha) + "/imagenes"
    )

    # Crear carpeta si no existen
    os.makedirs(carpeta, exist_ok=True)
    os.makedirs(imgcarpeta, exist_ok=True)

    try:
        # Decodificar la imagen desde base64
        image = Image.open(BytesIO(base64.b64decode(frame_detection)))

        # Convertir la imagen a bytes (por ejemplo, en formato PNG)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()
        file_img = os.path.join(imgcarpeta, f"{id_detection}.png")
        if not frame_detection:
            raise ValueError("La imagen está vacía.")

        with open(file_img, "wb") as fg:
            fg.write(img_bytes)


    except (ValueError, UnidentifiedImageError, base64.binascii.Error) as e:
        print(f"Error al procesar la imagen: {e}")

    # Ruta al archivo CSV
    csv_file = os.path.join(carpeta, "detections.csv")
    new_file = not os.path.exists(csv_file)
    clase_key = detection_class.lower()
    class_name = CLASSES.get(clase_key, {}).get("name", "indefinida").upper()

    # Escribir en el archivo CSV
    with open(csv_file, mode="a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(
                [
                    "id",
                    "camara",
                    "confianza",
                    "clase",
                    "tiempo",
                ]
            )
        writer.writerow(
            [id_detection, id_camera, confidence, class_name, time_detection]
        )


def logger_report(message):
    """
    Maneja los mensajes recibidos por WebSocket, decodifica los datos de los logs en formato JSON,
    y registra los datos en un archivo CSV.

    Args:
        websocket: Conexión WebSocket desde la cual se reciben los datos de los logs.
    """
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        print("Error al decodificar el JSON")
        return  # Usamos return en vez de continue porque no estamos en un loop

    # Se obtienen del JSON los valores necesarios
    traceback = data.get("traceback", "")
    sistema = data.get("sistema", "")
    fecha = datetime.now().strftime("%Y-%m-%d")

    carpeta = os.path.expanduser(f"" + PATH_LOGS + "/" + str(fecha))
    os.makedirs(carpeta, exist_ok=True)

    csv_file = os.path.join(carpeta, "logs.csv")
    new_file = not os.path.exists(csv_file)
    # Escribir en el archivo CSV
    with open(csv_file, mode="a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["fecha", "tipo sistema", "error"])
        writer.writerow([fecha, sistema, traceback])


# Configurar rutas y entorno
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DELETE_DAYS, PATH_STORAGE, WS_HOST, WS_PORT
from storage_controller import detection_report

# === CONFIGURACIÓN DE LIMPIEZA ===
base_detections_dir = PATH_STORAGE
days = DELETE_DAYS
waited_format = "%Y-%m-%d"


def try_rename(folder_path):
    """
    Intenta renombrar una carpeta cuyo nombre representa una fecha
    en formatos no estándar a un formato estándar 'YYYY-MM-DD'.

    Parámetros:
        folder_path (str): Ruta completa de la carpeta a renombrar.

    Retorna:
        str: Mensaje indicando si se renombró la carpeta, si ya tenía
             un nombre válido, o si no se pudo reconocer la fecha.
    """
    actual_name = os.path.basename(folder_path)

    # Si ya está bien formateado, no hacemos nada
    try:
        dt.datetime.strptime(actual_name, "%Y-%m-%d")
        return f"Nombre válido, sin cambios: '{actual_name}'"
    except:
        pass  # Continuamos a intentar otras conversiones

    # Intentar formatos comunes como día-mes-año
    posibles_formats = ["%d-%m-%Y", "%d_%m_%Y", "%Y_%m_%d", "%d %m %Y"]

    for fmt in posibles_formats:
        try:
            fecha = dt.datetime.strptime(actual_name, fmt)
            new_name = fecha.strftime("%Y-%m-%d")
            new_path = os.path.join(os.path.dirname(folder_path), new_name)

            if not os.path.exists(new_path):
                os.rename(folder_path, new_path)
                return f"Renombrada carpeta de '{actual_name}' a '{new_name}'"
            else:
                return f"No se renombró '{actual_name}' porque '{new_name}' ya existe."
        except:
            continue

    return f"No se pudo reconocer la fecha en: '{actual_name}'"


def delete_old_folders(detections_dir):
    """
    Elimina carpetas antiguas dentro de subdirectorios (como cam_1, cam_2...)
    si su nombre representa una fecha anterior al umbral de días definido.

    Parámetros:
        detections_dir (str): Ruta principal que contiene las carpetas de cámaras.

    Retorna:
        str: Informe con los resultados del proceso de limpieza y renombrado.
    """
    now = dt.datetime.now()
    threshold = now - dt.timedelta(days=days)
    mensajes = []

    if not os.path.exists(detections_dir):
        return f"Directorio {detections_dir} no existe."

    # Recorre cada subcarpeta (como cam_1, cam_2)
    for cam_folder in os.listdir(detections_dir):
        cam_path = os.path.join(detections_dir, cam_folder)
        if not os.path.isdir(cam_path):
            continue

        # Recorre carpetas dentro de cam_1, cam_2, etc.
        for subfolder in os.listdir(cam_path):
            subfolder_path = os.path.join(cam_path, subfolder)
            if not os.path.isdir(subfolder_path):
                continue

            result = try_rename(subfolder_path)
            mensajes.append(result)

            # Luego de intentar renombrar, obtenemos el nuevo nombre
            final_name = os.path.basename(subfolder_path)
            try:
                folder_date = dt.datetime.strptime(final_name, waited_format)
                if folder_date < threshold:
                    shutil.rmtree(subfolder_path)
                    mensajes.append(
                        f"Eliminada carpeta antigua: {final_name} en {cam_folder}"
                    )
            except Exception as e:
                mensajes.append(
                    f"Ignorada carpeta '{final_name}' en {cam_folder}, no tiene formato válido."
                )

    return "\n".join(mensajes)


async def execute_daily_task():
    """
    Programa la ejecución diaria de la función de limpieza automática
    a una hora específica definida por las constantes ERASE_HOUR,
    ERASE_MINUTE, ERASE_SECOND y ERASE_MSECOND.

    Se espera hasta la hora indicada y luego se ejecuta `delete_old_folders`.
    El proceso se repite diariamente.
    """
    while True:
        now = dt.datetime.now()
        target_time = now.replace(
            hour=ERASE_HOUR,
            minute=ERASE_MINUTE,
            second=ERASE_SECOND,
            microsecond=ERASE_MSECOND,
        )
        if now >= target_time:
            target_time += dt.timedelta(days=1)
        espera = (target_time - now).total_seconds()
        print(f"[INFO] Próxima limpieza de detections en {int(espera)} segundos.")
        await asyncio.sleep(espera)

        print("[INFO] Ejecutando limpieza automática de carpetas...")
        resultado = delete_old_folders(base_detections_dir)
        print("[LIMPIEZA AUTO]\n", resultado)


def delete_old_log_folders(logs_dir, day):
    """
    Elimina carpetas antiguas directamente dentro de logs_dir, usando como nombre de carpeta una fecha válida.

    Parámetros:
    logs_dir (str): Ruta a la carpeta 'logs'.
    day (int): Número de días de antigüedad para conservar.
    """
    now = datetime.now()
    threshold = now - timedelta(days=day)
    messages = []

    if not os.path.exists(logs_dir):
        return f"La carpeta '{logs_dir}' no existe."

    for folder in os.listdir(logs_dir):
        folder_path = os.path.join(logs_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        try:
            folder_date = datetime.strptime(folder, "%Y-%m-%d")
            if folder_date < threshold:
                shutil.rmtree(folder_path)
                messages.append(f"Eliminada carpeta antigua: {folder}")
        except ValueError:
            messages.append(
                f"Ignorada carpeta: {folder}, no tiene formato de fecha válido."
            )

    return "\n".join(messages)


async def execute_log_clean_task():
    """
    Programa una tarea automática para limpiar carpetas dentro de 'logs'.
    """
    from asyncio import sleep

    now = datetime.now()
    erase_time = now.replace(
        hour=ERASE_HOUR,
        minute=ERASE_MINUTE,
        second=ERASE_SECOND,
        microsecond=ERASE_MSECOND,
    )
    if erase_time < now:
        erase_time += timedelta(days=1)

    wait_seconds = (erase_time - now).total_seconds()
    print(f"Esperando {int(wait_seconds)} segundos para limpiar carpetas en 'logs'...")
    await sleep(int(wait_seconds))

    result = delete_old_log_folders(PATH_LOGS, day=DELETE_DAYS)
    print("[LIMPIEZA LOGS]", result)
