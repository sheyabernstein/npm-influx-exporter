import ipaddress
import socket
from datetime import datetime
from functools import lru_cache
from urllib.parse import urlparse

from npm_influx_exporter.cache import cached_with_ttl
from npm_influx_exporter.parse.patterns import HTTP_PATH_PATTERN
from npm_influx_exporter.settings import logger


def get_path_from_line(line: str) -> str | None:
    """
    Get the HTTP path from a log file's line

    Args:
        line: str of log file line

    Returns:
        str if path is found
    """
    if not line:
        return None

    match = HTTP_PATH_PATTERN.search(string=line)

    if not match:
        return None

    path = match.group(0).strip('"')

    if not path:
        return None

    try:
        result = urlparse(path)
    except Exception as e:
        logger.debug(f"Error getting url from {path}: {e}")
        return None

    return result.path or None


@lru_cache
def is_private_ip(address: str) -> bool:
    """
    Check if an IP address is a private local address

    Args:
        address: str of IP address

    Returns:
        bool if IP is private
    """
    try:
        ip = ipaddress.ip_address(address=address)
    except ValueError:
        return False

    return ip.is_private


@cached_with_ttl()
def get_ip_address_from_host(host: str) -> str:
    """
    Get the IP address for a host

    Args:
        host: str of host

    Returns:
        str of IP address
    """
    return socket.gethostbyname(host)


def convert_request_timestamp(timestamp: str) -> str:
    """
    Convert a log entry's timestamp to the format expected by Influxdb

    Args:
        timestamp: str of log timestamp

    Returns:
        str of formatted timestamp
    """
    dt = datetime.strptime(timestamp, "%d/%b/%Y:%H:%M:%S %z")
    tz_offset = dt.strftime("%z")
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f"{tz_offset[:-2]}:{tz_offset[-2:]}"
