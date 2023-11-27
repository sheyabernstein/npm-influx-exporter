from geoip2.models import City


def get_mock_city() -> City:
    return City(
        raw_response={
            "registered_country": {
                "geoname_id": 2077456,
                "iso_code": "AU",
                "names": {
                    "en": "Australia",
                },
            },
            "traits": {"ip_address": "1.1.1.1", "prefix_len": 32},
        }
    )
