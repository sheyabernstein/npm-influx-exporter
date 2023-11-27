from typing import List, Set

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from npm_influx_exporter.models.requests import Request
from npm_influx_exporter.objects import LimitedSizeSet
from npm_influx_exporter.settings import logger, settings

SEEN_REQUESTS: Set[Request] = LimitedSizeSet()


def export_requests(requests: List[Request]) -> int | None:
    """
    Export a list of requests to Influxdb

    Args:
        requests: list of Request objects

    Returns:
        int of exported requests count
    """

    if not requests:
        return None

    points = []

    for request in requests:
        if request in SEEN_REQUESTS:
            logger.debug(f"Skipping previously seen request {request}")
            continue

        point = Point(measurement_name=request.measurement_name.value)

        point.time(request.measurement_time)

        for key, value in request.point_tags.items():
            point.tag(key=key, value=value)

        for field, value in request.point_fields.items():
            point.field(field=field, value=value)

        points.append(point)
        SEEN_REQUESTS.add(request)

    if points:
        with InfluxDBClient(
            url=str(settings.INFLUX_URL),
            org=settings.INFLUX_ORG,
            token=settings.INFLUX_TOKEN.get_secret_value(),
        ) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket=settings.INFLUX_BUCKET, org=settings.INFLUX_ORG, record=points)

    return len(points)
