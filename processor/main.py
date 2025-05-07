import argparse
from processor_controller import process_detections
from json_handler import monitor_folder

if __name__ == "__main__":
    try:
        # Inicializar argumentos de entrada
        parser = argparse.ArgumentParser()
        parser.add_argument('--tiempo', type=int, default=900, help='tiempo de eliminación en segundos')
        option = parser.parse_args()
        observer = monitor_folder(
            tiempo= option.tiempo
        )
        process_detections()
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        observer.stop()
        observer.join()
    
