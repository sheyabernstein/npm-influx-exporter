from typing import Any, Dict, NamedTuple

from geoip2.models import City

from npm_influx_exporter.enums import RequestMeasurementNameEnum


class Request(NamedTuple):
    measurement_name: RequestMeasurementNameEnum
    measurement_time: str
    origin_ip: str
    target_ip: str
    target_domain: str
    http_status: int
    http_method: str
    path: str | None
    length: int | None
    city: City
    is_external: bool

    def __str__(self) -> str:
        return (
            f"{self.measurement_name.name} {self.measurement_time}"
            f" - {self.origin_ip} -> {self.target_domain}{self.path}"
        )

    def __hash__(self):
        return hash(
            (
                self.measurement_name,
                self.measurement_time,
                self.origin_ip,
                self.target_ip,
                self.target_domain,
            )
        )

    @property
    def point_tags(self) -> Dict[str, Any]:
        tags = {
            "IP": self.origin_ip,
            "Domain": self.target_domain,
            "Target": self.target_ip,
            "Path": self.path,
            "HTTPStatus": self.http_status,
            "HTTPMethod": self.http_method,
        }

        if self.is_external:
            tags.update(
                {
                    "key": self.city.country.iso_code,
                    "latitude": self.city.location.latitude,
                    "longitude": self.city.location.longitude,
                    "City": self.city.city.name,
                    "State": self.city.subdivisions.most_specific.name,
                    "Name": self.city.country.name,
                }
            )

        return tags

    @property
    def point_fields(self) -> Dict[str, Any]:
        fields = {
            "IP": self.origin_ip,
            "Domain": self.target_domain,
            "Target": self.target_ip,
            "Path": self.path,
            "HTTPStatus": self.http_status,
            "HTTPMethod": self.http_method,
            "length": self.length,
            "metric": 1,
        }

        if self.is_external:
            fields.update(
                {
                    "latitude": self.city.location.latitude,
                    "longitude": self.city.location.longitude,
                    "State": self.city.subdivisions.most_specific.name,
                    "City": self.city.city.name,
                    "key": self.city.country.iso_code,
                    "Name": self.city.country.name,
                }
            )

        return fields
