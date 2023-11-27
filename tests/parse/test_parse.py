from pathlib import Path
from unittest.mock import patch

import pytest

from npm_influx_exporter.enums import FileTypeEnum, RequestMeasurementNameEnum
from npm_influx_exporter.models.requests import Request
from npm_influx_exporter.parse.parse import _get_request_from_line
from tests.utils import get_mock_city


@pytest.mark.parametrize(
    ["line", "file_type", "expected_request"],
    [
        [
            "some malformed log line",
            FileTypeEnum.PROXY,
            None,
        ],
        [
            '[21/Nov/2023:00:00:14 +0000] - 200 201 - GET https www.google.com "/hi?k=v"'
            ' [Client 142.126.213.182] [Length 17365] [Gzip -] [Sent-to target] "curl/8.4.0" "-"',
            FileTypeEnum.PROXY,
            Request(
                measurement_name=RequestMeasurementNameEnum.REVERSE_PROXY,
                measurement_time="2023-11-21T00:00:14+00:00",
                origin_ip="142.126.213.182",
                target_ip="ip-from-host",
                target_domain="www.google.com",
                http_status=200,
                http_method="GET",
                path="/hi",
                length=17365,
                city=get_mock_city(),
                is_external=True,
            ),
        ],
        [
            '[27/Nov/2023:04:48:30 +0000] 301 - GET http dev.sheyabernstein.com "/?step=1"'
            ' [Client 159.223.48.151] [Length 166] [Gzip -] "Apache/2.4.34" "-"',
            FileTypeEnum.REDIRECT,
            Request(
                measurement_name=RequestMeasurementNameEnum.REDIRECT,
                measurement_time="2023-11-27T04:48:30+00:00",
                origin_ip="159.223.48.151",
                target_ip="redirect",
                target_domain="dev.sheyabernstein.com",
                http_status=301,
                http_method="GET",
                path="/",
                length=166,
                city=get_mock_city(),
                is_external=True,
            ),
        ],
    ],
    ids=[
        "unknown line",
        "proxy log line",
        "redirect log line",
    ],
)
@patch("npm_influx_exporter.parse.parse.geolocate_ip_address")
@patch("npm_influx_exporter.parse.parse.get_ip_address_from_host")
def test_get_request_from_line(
    mock_get_ip_address_from_host, mock_geolocate_ip_address, line, file_type, expected_request
):
    mock_geolocate_ip_address.return_value = get_mock_city()
    mock_get_ip_address_from_host.return_value = "ip-from-host"

    request = _get_request_from_line(
        line=line,
        file_type=file_type,
        file_path=Path(".log"),
    )

    assert request == expected_request
