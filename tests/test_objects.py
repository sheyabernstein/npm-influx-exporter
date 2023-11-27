import pytest

from npm_influx_exporter.objects import LimitedSizeSet


@pytest.mark.parametrize(
    ["max_size", "elements_to_add", "expected_result", "expected_queue"],
    [
        [3, [1, 2, 3], {1, 2, 3}, [1, 2, 3]],
        [3, [1, 2, 3, 4], {2, 3, 4}, [2, 3, 4]],
        [3, [3, 2, 1, 1, 2, 3], {1, 2, 3}, [1, 2, 3]],
        [3, [1, 2, 3, 4, 1], {3, 4, 1}, [3, 4, 1]],
    ],
    ids=[
        "unique elements that fit within the max size",
        "unique elements that exceed the max size",
        "duplicate elements fit within the max size",
        "duplicate elements that exceed the max size",
    ],
)
def test_limited_size_set(max_size, elements_to_add, expected_result, expected_queue):
    lss = LimitedSizeSet(max_size)

    lss.update(elements_to_add)

    assert len(lss) <= max_size
    assert set(lss) == expected_result
    assert list(lss.queue) == expected_queue
