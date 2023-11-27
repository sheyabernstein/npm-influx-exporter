import pytest
from geoip2.models import City

from npm_influx_exporter.settings import Settings, settings
from tests.utils import get_mock_city


@pytest.fixture(scope="session")
def settings_fixture() -> Settings:
    return settings


@pytest.fixture(name="mock_city")
def city_fixture() -> City:
    return get_mock_city()
