import logging
from pathlib import Path


def make_logger(
    name: str = "log",
    debug: bool = False,
    output: Path | None = None,
    quiet_stdout: bool | None = None,
) -> logging.Logger:  # pragma: no cover
    """
    Create a logger to help visualize program execution. This method will always
    return a logger with a StreamHandler object unless specified through the
    parameters.

    Args:
        name: The name to give to the logger.
        debug: Whether to enable debug mode.
        output: The directory to store the log file. Will attach a FileHandler to the logger.
        quiet_stdout: Do not attach a StreamHandler object to the logger.
    Returns:
        A logging object
    """
    level: int = logging.DEBUG if debug else logging.INFO
    log = logging.getLogger(name)
    if not log.hasHandlers():
        log.setLevel(level)
        format_string: str = (
            f"%(asctime)s - %(levelname)s {'- %(funcName)s' if debug else ''} - " f"%(message)s"
        )
        formatter = logging.Formatter(format_string)
        no_stdout: bool = quiet_stdout is None and output is not None
        if output:
            output.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(filename=str(output / f"{name}.log"))
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            log.addHandler(file_handler)
        if not no_stdout:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(level)
            stream_handler.setFormatter(formatter)
            log.addHandler(stream_handler)
        if not output and quiet_stdout:
            raise ValueError("All loggers suppressed, while there should be at least one enabled!")
    return log
