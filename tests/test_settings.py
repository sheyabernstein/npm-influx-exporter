import os
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError

from npm_influx_exporter.settings import Settings


@pytest.mark.parametrize(
    ["file_contents", "expected_ips"],
    [
        [
            """
            # one.com
            1.1.1.1

            10.10.10.1
            """,
            {"1.1.1.1", "10.10.10.1"},
        ],
        [
            "",
            set(),
        ],
    ],
    ids=[
        "load without comments",
        "empty file",
    ],
)
def test_settings_init_load_monitor_ips(file_contents, expected_ips):
    settings_kwargs = {}

    file = NamedTemporaryFile(delete=False)
    settings_kwargs["MONITOR_IP_PATH"] = Path(file.name)
    with open(file.name, "w") as fp:
        fp.write(file_contents)

    settings = Settings(MONITOR_IP_PATH=Path(file.name))
    assert settings.MONITOR_IP_ADDRESSES == expected_ips

    if file:
        os.remove(file.name)


@pytest.mark.parametrize(
    ["status_code", "fake_external_ip", "expected_result"],
    [
        [200, "1.1.1.1", "1.1.1.1"],
        [400, "8.8.8.8", None],
    ],
    ids=["http ok", "http error"],
)
def test_get_external_ip(
    settings_fixture, status_code, fake_external_ip, expected_result, monkeypatch
):
    with patch("npm_influx_exporter.settings.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = fake_external_ip
        mock_response.status_code = status_code
        mock_get.return_value = mock_response

        if status_code != 200:
            mock_response.raise_for_status.side_effect = HTTPError("Fake HTTPError")

        if status_code == 200:
            result = settings_fixture.get_external_ip()
            assert result == expected_result

        else:
            with pytest.raises(HTTPError):
                result = settings_fixture.get_external_ip()
                assert result == expected_result

        mock_get.assert_called_once()

        if status_code != 200:
            mock_response.raise_for_status.assert_called_once()


@pytest.mark.parametrize(
    ["last_refresh", "refresh_after_minutes", "expected_result"],
    [
        [None, 10, True],
        [datetime.now() - timedelta(minutes=5), 10, False],
        [datetime.now() - timedelta(minutes=15), 10, True],
    ],
    ids=[
        "None, refresh",
        "within threshold, don't refresh",
        "outside threshold, refresh",
    ],
)
def test_external_ip_needs_refresh(
    settings_fixture, last_refresh, refresh_after_minutes, expected_result, caplog
):
    settings_fixture.last_external_ip_refresh = last_refresh
    settings_fixture.REFRESH_EXTERNAL_IP_AFTER_MINUTES = refresh_after_minutes

    result = settings_fixture.external_ip_needs_refresh

    assert result == expected_result
