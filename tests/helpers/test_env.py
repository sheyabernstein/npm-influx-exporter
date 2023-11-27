import pytest

from npm_influx_exporter.helpers.env import get_env_bool


@pytest.mark.parametrize(
    ["env_name", "default", "env_value", "expected_result"],
    [
        ["TEST_ENV", False, None, False],
        ["TEST_ENV", True, None, True],
        ["TEST_ENV", False, "False", False],
        ["TEST_ENV", False, "true", True],
        ["TEST_ENV", False, "invalid", False],
        ["TEST_ENV", True, "invalid", True],
    ],
    ids=[
        "missing environment variable and default value",
        "missing environment variable and default value as True",
        "environment variable set to False",
        "environment variable set to True",
        "invalid environment variable, should default to False",
        "invalid environment variable, should default to True",
    ],
)
def test_get_env_bool(env_name, default, env_value, expected_result, monkeypatch):
    if env_value is not None:
        monkeypatch.setenv(env_name, env_value)
    else:
        monkeypatch.delenv(env_name, raising=False)

    result = get_env_bool(env_name, default)
    assert result == expected_result
