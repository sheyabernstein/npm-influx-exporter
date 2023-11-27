import pytest

from npm_influx_exporter.cache import cached_with_ttl


@cached_with_ttl()
def example_function(value):
    print(f"example_function called with {value}")
    return value


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        [1, 1],
        ["hello", "hello"],
    ],
)
def test_cached_with_ttl(input_value, expected_output, capfd):
    expected_stdout = f"example_function called with {input_value}"

    example_function(input_value)
    assert expected_stdout in capfd.readouterr().out

    result = example_function(input_value)
    assert expected_stdout not in capfd.readouterr().out

    assert result == expected_output
