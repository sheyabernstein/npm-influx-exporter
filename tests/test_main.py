import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch
from uuid import uuid4

import pytest

from npm_influx_exporter.enums import FileTypeEnum
from npm_influx_exporter.main import process_log_files
from npm_influx_exporter.settings import settings


@pytest.mark.parametrize(
    ["file_has_contents", "request_count"],
    [
        [True, 0],
        [True, 10],
        [False, 0],
        [False, 10],
    ],
)
@patch("npm_influx_exporter.main.get_requests_from_file")
@patch("npm_influx_exporter.main.export_requests")
def test_process_log_files(
    mock_export_requests, mock_get_requests_from_file, file_has_contents, request_count, caplog
):
    file_type = FileTypeEnum.PROXY
    file = NamedTemporaryFile(delete=False)

    if file_has_contents:
        with open(file.name, "w") as fp:
            fp.write(str(uuid4()))

    path = Path(file.name)
    requests = [i for i in range(request_count)]
    mock_get_requests_from_file.return_value = requests

    settings.NPM_LOGS_DIR = path.parent
    process_log_files(pattern=path.name, file_type=file_type)

    if file_has_contents:
        mock_get_requests_from_file.assert_called_once_with(
            file_path=path,
            file_type=file_type,
        )
    else:
        mock_export_requests.assert_not_called()
        assert f"ignoring empty file {path.name}" in caplog.text.lower()

    if file_has_contents and requests:
        mock_export_requests.assert_called_once_with(requests=requests)
    else:
        mock_export_requests.assert_not_called()

    os.remove(path)
