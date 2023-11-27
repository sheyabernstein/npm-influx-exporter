from datetime import datetime
from pathlib import Path
from typing import Set

import requests
from pydantic import AnyUrl, Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from npm_influx_exporter.helpers.env import get_env_bool
from npm_influx_exporter.helpers.logging import make_logger

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DEBUG: bool = get_env_bool("DEBUG", default=False)

    INFLUX_URL: AnyUrl
    INFLUX_ORG: str
    INFLUX_BUCKET: str
    INFLUX_TOKEN: SecretStr

    EXPORT_INTERNAL_REQUESTS: bool = False
    EXPORT_MONITORING_LOGS: bool = False

    LOGS_DIR: Path = Field(default=BASE_DIR / "logs")
    NPM_LOGS_DIR: Path = Field(default=BASE_DIR / "data/logs")
    GEO_DATABASE_PATH: Path = Field(default=BASE_DIR / "data/geolite/GeoLite2-City.mmdb")
    MONITOR_IP_PATH: Path = Field(default=BASE_DIR / "data/monitors/ip_addresses.txt")

    READ_LAST_N_LINES: PositiveInt = Field(default=50)
    SLEEP_BETWEEN_SECONDS: PositiveInt = Field(default=1)
    REFRESH_EXTERNAL_IP_AFTER_MINUTES: PositiveInt = Field(default=60)

    EXTERNAL_IP_ADDRESS: str | None = None
    MONITOR_IP_ADDRESSES: Set[str] = Field(default_factory=list)

    last_external_ip_refresh: datetime | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    def __init__(self, **data):
        super().__init__(**data)

        if self.MONITOR_IP_PATH.exists():
            # load monitor IP addresses
            with open(self.MONITOR_IP_PATH, "r") as fp:
                lines = {x.strip() for x in fp.readlines()}
                self.MONITOR_IP_ADDRESSES = {x for x in lines if x and not x.startswith("#")}

    def get_external_ip(self):
        """
        Get the current external IP address

        Returns:
            str of external IP address
        """
        logger.info(
            f"{'Refreshing' if self.EXTERNAL_IP_ADDRESS else 'Getting'} external IP address"
        )

        r = requests.get(url="https://api.ipify.org")
        r.raise_for_status()

        external_ip = r.text
        logger.info(f"External IP address is {external_ip}")
        self.EXTERNAL_IP_ADDRESS = external_ip
        self.last_external_ip_refresh = datetime.now()
        return external_ip

    @property
    def external_ip_needs_refresh(self) -> bool:
        if self.last_external_ip_refresh is None:
            return True

        last_refresh = (datetime.now() - self.last_external_ip_refresh).seconds
        return last_refresh / 60 >= self.REFRESH_EXTERNAL_IP_AFTER_MINUTES


settings = Settings()

logger = make_logger(
    name="app",
    debug=settings.DEBUG,
    output=settings.LOGS_DIR,
    quiet_stdout=False,
)

settings.get_external_ip()
