from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from npm_influx_exporter.parse.helpers import (
    convert_request_timestamp,
    get_ip_address_from_host,
    get_path_from_line,
    is_private_ip,
)


@pytest.mark.parametrize(
    ["line", "expected_path"],
    [
        [
            '[21/Nov/2023:00:00:14 +0000] - 200 201 - GET https www.google.com "/hi?k=v"'
            ' [Client 142.126.213.182] [Length 17365] [Gzip -] [Sent-to target] "curl/8.4.0" "-"',
            "/hi",
        ],
        ['+0000] - 200 201 - GET https www.google.com "/h', None],
        [None, None],
    ],
    ids=[
        "valid line",
        "invalid line",
        "no line",
    ],
)
def test_get_path_from_line(line, expected_path):
    path = get_path_from_line(line=line)
    assert path == expected_path


@pytest.mark.parametrize(
    ["is_private", "expected_result"],
    [[True, True], [False, False]],
    ids=[
        "private",
        "not private",
    ],
)
@patch("npm_influx_exporter.parse.helpers.ipaddress.ip_address")
def test_is_private_ip(mock_ip_address, is_private, expected_result):
    ip = str(uuid4())
    is_private_mock = Mock
    is_private_mock.is_private = is_private
    mock_ip_address.return_value = is_private_mock

    is_private_ip(address=ip)
    result = is_private_ip(address=ip)

    assert result == expected_result

    # the underlying call should be cached
    mock_ip_address.assert_called_once_with(address=ip)


def test_is_private_ip__invalid_address():
    result = is_private_ip(address="not-an-ip")
    assert result is False


@patch("npm_influx_exporter.parse.helpers.socket.gethostbyname")
def test_get_ip_address_from_host(mock_get_host_by_name):
    host = "my-host"
    ip = "host-ip"
    mock_get_host_by_name.return_value = ip

    get_ip_address_from_host(host=host)
    result = get_ip_address_from_host(host=host)

    assert result == ip

    # the underlying call should be cached
    mock_get_host_by_name.assert_called_once_with(host)


@pytest.mark.parametrize(
    ["timestamp", "expected_timestamp"],
    [
        ["21/Nov/2023:01:50:48 +0000", "2023-11-21T01:50:48+00:00"],
    ],
)
def test_convert_request_timestamp(timestamp, expected_timestamp):
    assert convert_request_timestamp(timestamp=timestamp) == expected_timestamp
