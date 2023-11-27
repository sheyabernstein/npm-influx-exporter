from pathlib import Path
from typing import List

from npm_influx_exporter.enums import FileTypeEnum, RequestMeasurementNameEnum
from npm_influx_exporter.helpers.files import get_file_last_n_lines
from npm_influx_exporter.helpers.geolocate import geolocate_ip_address
from npm_influx_exporter.models.requests import Request
from npm_influx_exporter.parse.helpers import (
    convert_request_timestamp,
    get_ip_address_from_host,
    get_path_from_line,
    is_private_ip,
)
from npm_influx_exporter.parse.patterns import (
    HTTP_METHOD_PATTERN,
    HTTP_STATUS_PATTERN,
    IP_PATTERN,
    LENGTH_PATTERN,
    TARGET_DOMAIN_PATTERN,
    TIMESTAMP_PATTERN,
)
from npm_influx_exporter.settings import logger, settings


def _get_request_from_line(line: str, file_type: FileTypeEnum, file_path: Path) -> Request | None:
    """
    Get a Request for a log file's line

    Args:
        line: str of line
        file_type: FileTypeEnum enum
        file_path: Path to file

    Returns:
        Request object if one can be parsed from the line
    """
    target_ip_match = IP_PATTERN.search(line)
    target_domain_match = TARGET_DOMAIN_PATTERN.search(line)
    timestamp_match = TIMESTAMP_PATTERN.search(line)

    if target_domain_match:
        target_domain = target_domain_match.group("domain")
    else:
        logger.debug(f"Unable to detect a target domain in line for file {file_path.name}: {line}")
        return

    if not timestamp_match:
        logger.debug(f"Unable to detect a timestamp for file {file_path.name}: {line}")
        return

    length = None
    length_match = LENGTH_PATTERN.search(line)

    is_external_request = True
    measurement_name: RequestMeasurementNameEnum | None = None
    measurement_time = convert_request_timestamp(timestamp=timestamp_match.group())

    is_redirect = file_type == FileTypeEnum.REDIRECT
    origin_ip = IP_PATTERN.search(line).group(1) if target_ip_match else None

    if length_match:
        length = int(length_match.group())

    if origin_ip and (
        origin_ip == settings.EXTERNAL_IP_ADDRESS or is_private_ip(address=origin_ip)
    ):
        is_external_request = False
        logger.debug(f"Internal IP Source: {origin_ip} called {target_domain}")
        if settings.EXPORT_INTERNAL_REQUESTS:
            measurement_name = RequestMeasurementNameEnum.INTERNAL_REVERSE_PROXY
    elif origin_ip in settings.MONITOR_IP_ADDRESSES:
        logger.debug(f"Excluded monitoring service {origin_ip} checked {target_domain}")
        if settings.EXPORT_MONITORING_LOGS:
            measurement_name = RequestMeasurementNameEnum.MONITORING_REVERSE_PROXY
    else:
        measurement_name = (
            RequestMeasurementNameEnum.REDIRECT
            if is_redirect
            else RequestMeasurementNameEnum.REVERSE_PROXY
        )

    if not measurement_name:
        return

    city = geolocate_ip_address(ip_address=origin_ip)

    if not city:
        return

    http_method_match = HTTP_METHOD_PATTERN.search(line)
    http_status_match = HTTP_STATUS_PATTERN.search(line)

    return Request(
        measurement_name=measurement_name,
        measurement_time=measurement_time,
        origin_ip=origin_ip,
        target_ip="redirect" if is_redirect else get_ip_address_from_host(host=target_domain),
        target_domain=target_domain,
        http_method=http_method_match.group() if http_method_match else None,
        http_status=int(http_status_match.group("status")) if http_status_match else None,
        path=get_path_from_line(line=line),
        length=length,
        city=city,
        is_external=is_external_request,
    )


def get_requests_from_file(
    file_path: Path, file_type: FileTypeEnum, n_lines: int = settings.READ_LAST_N_LINES
) -> List[Request]:
    """
    Parse a list of Request objects from a file

    Args:
        file_path: Path to file
        file_type: FileTypeEnum enum
        n_lines: int of last n lines to read

    Returns:
        list of parsed Request objects
    """

    requests = []
    lines = get_file_last_n_lines(file_path=file_path, n=n_lines)

    for line in lines:
        try:
            request = _get_request_from_line(
                line=line,
                file_type=file_type,
                file_path=file_path,
            )
        except Exception as e:
            logger.debug(f"Error getting request from line om file {file_path.name}: {e}")
            continue

        if request:
            requests.append(request)

    return requests
