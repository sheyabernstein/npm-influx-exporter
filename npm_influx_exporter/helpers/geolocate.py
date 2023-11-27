import socket

from geoip2.database import Reader
from geoip2.models import City

from npm_influx_exporter.cache import cached_with_ttl
from npm_influx_exporter.settings import logger, settings

if settings.GEO_DATABASE_PATH.exists():
    GEOIP_DATABASE = Reader(fileish=settings.GEO_DATABASE_PATH)
else:
    GEOIP_DATABASE = None


@cached_with_ttl()
def get_ip_from_hostname(hostname: str) -> str:
    """
    Get an IP address from a hostname

    Args:
        hostname: str of hostname

    Returns:
        str of IP address
    """
    logger.debug(f"Resolving IP address for host {hostname}")
    return socket.gethostbyname(hostname)


@cached_with_ttl()
def geolocate_ip_address(ip_address: str) -> City | None:
    """
    Get the city for an IP address

    Args:
        ip_address: str of IP address

    Returns:
        geoip2 City of geolocated city
    """
    if GEOIP_DATABASE is None:
        logger.error(
            f"Error geolocating {ip_address}: Database not found at {settings.GEO_DATABASE_PATH}"
        )
        return None

    logger.debug(f"Geolocating {ip_address}")

    try:
        return GEOIP_DATABASE.city(ip_address=ip_address)
    except Exception as e:
        logger.error(f"Error getting location for {ip_address}: {e}")

    return None
