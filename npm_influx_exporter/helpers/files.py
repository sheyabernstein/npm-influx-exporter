from pathlib import Path
from typing import List

from npm_influx_exporter.settings import logger


def get_file_last_n_lines(file_path: Path, n: int = 100, chunk_size=1024) -> List[str]:
    """
    Get the last n lines from a file

    Args:
        file_path: Path of file
        n: int of lines to read, defaults to 100
        chunk_size: int of chunk size

    Returns:
        list of line strings
    """
    if not file_path.exists():
        logger.error(f"Tried reading files from non-existent file: {file_path}")
        return []

    with open(file_path, "rb") as file:
        file.seek(0, 2)
        file_size = file.tell()

        lines = []
        remaining_bytes = min(file_size, chunk_size)
        while remaining_bytes > 0 and len(lines) < n:
            file.seek(-remaining_bytes, 2)
            chunk = file.read(remaining_bytes).decode()
            lines = chunk.splitlines(True) + lines
            remaining_bytes = min(file_size, remaining_bytes + chunk_size)

        return [x.strip() for x in lines[-n:]]
