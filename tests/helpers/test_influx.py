from unittest.mock import patch

import pytest
from geoip2.models import City

from npm_influx_exporter.enums import RequestMeasurementNameEnum
from npm_influx_exporter.helpers.influx import SEEN_REQUESTS, export_requests
from npm_influx_exporter.models.requests import Request
from npm_influx_exporter.settings import settings

request = Request(
    measurement_name=RequestMeasurementNameEnum.REVERSE_PROXY,
    measurement_time="time",
    origin_ip="origin",
    target_ip="target",
    target_domain="target",
    http_status=200,
    http_method="GET",
    length=0,
    path="/",
    city=City(raw_response={}),
    is_external=True,
)


@pytest.mark.parametrize(
    ["requests", "seen_requests", "expected_count", "expected_seen_count"],
    [
        [[], [], None, 0],
        [[request], [], 1, 1],
        [[request, request], [], 1, 1],
        [[request], [request], 0, 1],
    ],
    ids=[
        "no requests",
        "one request",
        "duplicate requests",
        "previously seen request",
    ],
)
@patch("npm_influx_exporter.helpers.influx.InfluxDBClient")
def test_export_requests(mock_client, requests, seen_requests, expected_count, expected_seen_count):
    SEEN_REQUESTS.clear()

    if seen_requests:
        SEEN_REQUESTS.update(seen_requests)

    exported_count = export_requests(requests=requests)

    assert exported_count == expected_count
    assert len(SEEN_REQUESTS) == expected_seen_count

    if expected_count:
        mock_client.assert_called_with(
            url=str(settings.INFLUX_URL),
            org=settings.INFLUX_ORG,
            token=settings.INFLUX_TOKEN.get_secret_value(),
        )
