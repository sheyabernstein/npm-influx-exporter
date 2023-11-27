from time import sleep

from npm_influx_exporter.enums import FileTypeEnum
from npm_influx_exporter.helpers.influx import export_requests
from npm_influx_exporter.parse import get_requests_from_file
from npm_influx_exporter.settings import logger, settings


def process_log_files(pattern: str, file_type: FileTypeEnum) -> None:
    """
    Process log files

    Args:
        pattern: str of file pattern
        file_type: FileTypeEnum enum

    Returns:
        None
    """

    for log_file_path in settings.NPM_LOGS_DIR.glob(pattern):
        if not log_file_path.stat().st_size:
            logger.debug(f"Ignoring empty file {log_file_path.name}")
            continue

        logger.debug(f"Processing {file_type} file: {log_file_path.name}")
        requests = get_requests_from_file(file_path=log_file_path, file_type=file_type)
        logger.debug(f"Found {len(requests)} requests in {log_file_path.name}")

        if not requests:
            continue

        export_count = export_requests(requests=requests)
        logger.debug(f"Exported {export_count} requests in file: {log_file_path.name}")


def run():
    logger.info("Starting NPM Influx Exporter")

    if settings.DEBUG:
        logger.info("Debug: on")

    while True:
        if settings.external_ip_needs_refresh:
            settings.get_external_ip()

        process_log_files(pattern="proxy-host-*_access.log", file_type=FileTypeEnum.PROXY)
        process_log_files(pattern="redirection-host-*_access.log", file_type=FileTypeEnum.REDIRECT)

        logger.debug(f"Sleeping for {settings.SLEEP_BETWEEN_SECONDS} seconds")
        sleep(settings.SLEEP_BETWEEN_SECONDS)


if __name__ == "__main__":
    run()
