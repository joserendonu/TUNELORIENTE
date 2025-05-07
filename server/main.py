import asyncio
import json
import threading
from websockets.server import serve

from config import WS_HOST, WS_PORT
from storage_controller import detection_report, execute_daily_task, execute_log_clean_task, logger_report
from alert_controller import plot_dispatcher, root

async def handle_logs(websocket):
    """
    Se Manejan los mensajes entrantes en la ruta '/logs'.
    Se usa este import(websockets.server)porque es el que nos permite usar el path 
    de la URL
    Se Reciben mensajes del cliente a través del WebSocket, los imprime como logs
    y responde confirmando la recepción del log.
    Args:
        websocket (WebSocketServerProtocol): Conexión WebSocket activa.
        Tenemos la función cuando se requiere un log del servidor
    """
    async for message in websocket:
        # print(f"[LOG] {message}")
        logger_report(message)
        await websocket.send("Log recibid")

async def handle_detections(websocket):   
    """
    Maneja los mensajes entrantes en la ruta '/detections'.

    Recibe mensajes del cliente a través del WebSocket, los imprime como detecciones
    y responde confirmando la recepción de la detección.

    Args:
        websocket (WebSocketServerProtocol): Conexión WebSocket activa.
        Tenemos la función cuando se requiere una detection del servidor
    """
    async for message in websocket:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("Error al decodificar el JSON")
            return  # Usamos return en vez de continue porque no estamos en un loop
    
        # Se obtienen del JSON los valores necesarios
        caid = data.get("nombre_camara", "")
        id = data.get("id", "")
        frame = data.get("imagen", "")
        confidence = data.get("confianza", 0.0)
        detection_class = data.get("clase", "")
        detection_time = data.get("tiempo", "")
        detection_report(id, caid, frame, confidence, detection_class, detection_time)
        plot_dispatcher(caid, detection_time,detection_class, frame)
        await websocket.send("Detección recibida") 

async def main_handler(websocket, path):
    """
    Enruta la conexión WebSocket al handler correspondiente según el path.

    Si el path es '/logs' o '/detections', delega el manejo al handler adecuado.
    En caso contrario, envía un mensaje de error y cierra la conexión.

    Args:
        websocket (WebSocketServerProtocol): Conexión WebSocket activa.
        path (str): Ruta solicitada por el cliente.
    """
    print(f"Cliente conectado a {path}")
    if path == "/logs":
        await handle_logs(websocket)
    elif path == "/detections":
        await handle_detections(websocket)
    else:
        await websocket.send("Ruta no válida")
        await websocket.close()

# === INICIAR SERVIDOR Y TAREA PROGRAMADA ===

async def main():
    """
    Inicia el servidor WebSocket en la ip y puerto definido.

    Escucha conexiones entrantes indefinidamente.
    Ejecutar tarea diaria se encarga de
    Elimina las carpetas con fechas anteriores a 30 días antes de today dentro del directorio de un cam_id.
    """
    async with serve(main_handler, WS_HOST, WS_PORT):
        print(f"Servidor WebSocket escuchando en ws://{WS_HOST}:{WS_PORT}")
        await asyncio.gather(
            execute_daily_task(),
            execute_log_clean_task(),
            
            asyncio.Future()  # Mantener activo el servidor
        )


def run_asyncio_loop():
    asyncio.run(main())

if __name__ == "__main__":
    """
    Para que las pruebas unitarias no se queden corriendo indefinidamente se usa
    esto en vez de asyncio.run(main())
    """
    threading.Thread(target=run_asyncio_loop, daemon=True).start()
    root.mainloop()
