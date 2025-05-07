import json
import pytest
from unittest import mock
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from server.storage_controller import detection_report

@mock.patch("server.storage_controller.plot_dispatcher")
@mock.patch("server.storage_controller.os.makedirs")
@mock.patch("server.storage_controller.open", new_callable=mock.mock_open)
@mock.patch("server.storage_controller.Image.open")
@mock.patch("server.storage_controller.os.path.exists", return_value=False)
@mock.patch("server.storage_controller.os.path.expanduser", side_effect=lambda x: x.replace("~", "/home/user"))
def test_detection_report(
    mock_expanduser,
    mock_exists,
    mock_image_open,
    mock_open,
    mock_makedirs,
    mock_plot_dispatcher,
):
    # Preparamos un mensaje simulado
    message = json.dumps({
        "id": "test123",
        "nombre_camara": "camara_test",
        "imagen": "aGVsbG8=",  # base64 de "hello"
        "confianza": 0.95,
        "clase": "Bicycle",
        "tiempo": "12:00"
    })

    # Simulamos Image.open devolviendo un objeto que tiene save
    mock_image = mock.Mock()
    mock_image.save = mock.Mock()
    mock_image_open.return_value = mock_image

    # Ejecutamos la función
    detection_report(message)

    # Verificar que se crearon las carpetas
    assert mock_makedirs.call_count >= 1

    # Verificar que se haya abierto un archivo
    assert mock_open.called

    # Verificar que se llamó plot_dispatcher
    assert mock_plot_dispatcher.called
