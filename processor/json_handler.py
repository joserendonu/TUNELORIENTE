import os
import time
import threading

from config import BASE_DIR
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class JSONHandler(FileSystemEventHandler):
    """
    Clase para manejar eventos de eliminación de archivos JSON en una carpeta específica.

    attributes:
        tiempo (int): Tiempo en segundos antes de eliminar el archivo JSON.
            Por defecto es 900 segundos (15 minutos).
    """
    def __init__(
        self,
        carpeta: str = None,
        tiempo: int = 900,  # 15 minutos
    ) -> None:
        self.carpeta = carpeta
        self.tiempo = tiempo


    def on_created(self, event) -> None:
        """
        Método que se llama cuando se crea un nuevo archivo en la carpeta monitoreada.
        Si el archivo es un JSON, se programa su eliminación después de un tiempo definido.    
        """
        if not event.is_directory and event.src_path.endswith('.json'):
            file_path = event.src_path
            print(f"Nuevo archivo JSON: {os.path.basename(file_path)}")
            self.schedule_deletion(file_path)


    def schedule_deletion(self, file_path) -> None:
        """
        Programa la eliminación del archivo JSON después de un tiempo definido.
        
        args:
            file_path (str): Ruta del archivo JSON a eliminar
        """
        def delete_file():
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Eliminado: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"Error de eliminación {file_path}: {str(e)}")
        
        timer = threading.Timer(self.tiempo, delete_file)
        timer.start()
        print(f"Eliminación programada: {os.path.basename(file_path)}")


def monitor_folder(
        carpeta: str = str(BASE_DIR.resolve()),
        tiempo: int = 900
    ) -> None:
    """
    Monitorea una carpeta en busca de archivos JSON y los elimina después de un
    tiempo, definido en segundos.

    args:
        tiempo (int): Tiempo en segundos antes de eliminar el archivo JSON.
            Por defecto es 900 segundos (15 minutos).
    """

    event_handler = JSONHandler(
        carpeta = carpeta,
        tiempo = tiempo
    )
    observer = Observer()
    observer.schedule(event_handler, carpeta, recursive=False)
    observer.start()
    
    print(f"Monitoreando carpeta: {carpeta}")
    return observer
