from enum import Enum


class FileTypeEnum(str, Enum):
    PROXY = "proxy"
    REDIRECT = "redirect"


class RequestMeasurementNameEnum(str, Enum):
    REDIRECT = "Redirections"
    REVERSE_PROXY = "ReverseProxyConnections"
    INTERNAL_REVERSE_PROXY = "InternalRProxyIPs"
    MONITORING_REVERSE_PROXY = "MonitoringRProxyIPs"
