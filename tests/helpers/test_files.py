import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

import pytest

from npm_influx_exporter.helpers.files import get_file_last_n_lines

TEST_FILE_CONTENT = "\n".join([f"Line {i}" for i in range(1, 201)]).encode()


@pytest.mark.parametrize(
    ["n", "expected_lines"],
    [
        (5, [f"Line {i}" for i in range(196, 201)]),
        (10, [f"Line {i}" for i in range(191, 201)]),
        (100, [f"Line {i}" for i in range(101, 201)]),
        (200, [f"Line {i}" for i in range(1, 201)]),
    ],
    ids=[
        "n=5",
        "n=10",
        "n=100",
        "n=200",
    ],
)
def test_get_file_last_n_lines(n, expected_lines):
    with NamedTemporaryFile(delete=False) as file:
        file.write(TEST_FILE_CONTENT)

    file_path = Path(file.name)
    result = get_file_last_n_lines(file_path, n)
    assert len(result) == len(expected_lines)
    os.remove(file_path)


def test_get_file_last_n_lines__non_existent_file(caplog):
    result = get_file_last_n_lines(
        file_path=Path(str(uuid4())),
    )
    assert result == []
    assert "tried reading files from non-existent file" in caplog.text.lower()
