import json
import pytest
from unittest import mock
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from server.storage_controller import logger_report

@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("os.makedirs")
@mock.patch("os.path.exists", return_value=False)
@mock.patch("os.path.expanduser", side_effect=lambda x: x.replace("~", "/home/user"))
@mock.patch("csv.writer")
def test_logger_report(mock_csv_writer, mock_expanduser, mock_exists, mock_makedirs, mock_open):
    # Preparamos un mensaje de entrada válido
    message = json.dumps({
        "traceback": "Error simulado",
        "sistema": "SistemaTest"
    })

    # Llamamos a la función
    logger_report(message)

    # Verificamos que se haya intentado crear la carpeta
    assert mock_makedirs.called

    # Verificamos que open fue llamado para crear el CSV
    assert mock_open.called

    # Verificamos que se escribió en el CSV
    writer_instance = mock_csv_writer.return_value
    assert writer_instance.writerow.call_count >= 1