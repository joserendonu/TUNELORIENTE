import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import sys
import os
from websockets import WebSocketServerProtocol
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


from server.main import handle_logs, handle_detections, main_handler
# from server.config import ...


@pytest.mark.asyncio
async def test_handle_logs():
    """
    Prueba que la función handle_logs reciba un mensaje y responda correctamente.

    Verifica que se llame a websocket.send con "Log recibido".
    """
    websocket = AsyncMock()
    websocket.__aiter__.return_value = ["mensaje de prueba"]

    await handle_logs(websocket)

    websocket.send.assert_called_with("Log recibido")

@pytest.mark.asyncio
async def test_handle_detections():
    """
    Prueba que la función handle_detections reciba un mensaje y responda correctamente.

    Verifica que se llame a websocket.send con "Detección recibida".
    """
    websocket = AsyncMock()
    websocket.__aiter__.return_value = ["mensaje de prueba"]

    await handle_detections(websocket)

    websocket.send.assert_called_with("Detección recibida")

@pytest.mark.asyncio
async def test_main_handler_invalid_path():
    """
    Prueba que main_handler maneje correctamente una ruta inválida.

    Verifica que se envíe el mensaje de error y se cierre la conexión.
    """
    websocket = AsyncMock()
    path = "/invalid"

    await main_handler(websocket, path)

    websocket.send.assert_awaited_once_with("Ruta no válida")
    websocket.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_main_handler_logs():
    """
    Prueba que main_handler invoque handle_logs cuando el path es '/logs'.

    Verifica que se llame una vez a handle_logs con el websocket simulado.
    """
    websocket = AsyncMock()
    path = "/logs"

    with patch("server.main.handle_logs", new_callable=AsyncMock) as mock_handle_logs:
        await main_handler(websocket, path)
        mock_handle_logs.assert_awaited_once_with(websocket)

@pytest.mark.asyncio
async def test_main_handler_detections():
    """
    Prueba que main_handler invoque handle_detections cuando el path es '/detections'.

    Verifica que se llame una vez a handle_detections con el websocket simulado.
    """
    websocket = AsyncMock()
    path = "/detections"

    with patch("server.main.handle_detections", new_callable=AsyncMock) as mock_handle_detections:
        await main_handler(websocket, path)
        mock_handle_detections.assert_awaited_once_with(websocket)