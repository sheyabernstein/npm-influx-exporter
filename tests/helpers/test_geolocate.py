from unittest.mock import MagicMock, patch

from npm_influx_exporter.helpers.geolocate import (
    geolocate_ip_address,
    get_ip_from_hostname,
)


@patch("npm_influx_exporter.helpers.geolocate.socket.gethostbyname")
def test_get_ip_from_hostname(mock_get_host_by_name):
    hostname = "host"
    mock_get_host_by_name.return_value = hostname

    result = get_ip_from_hostname(hostname=hostname)

    assert result == hostname
    mock_get_host_by_name.assert_called_once_with(hostname)


def test_geolocate_ip_address():
    with patch(
        "npm_influx_exporter.helpers.geolocate.GEOIP_DATABASE", new=MagicMock()
    ) as mock_database:
        geolocate_ip_address("1.1.1.1")

    mock_database.city.assert_called_with(ip_address="1.1.1.1")
