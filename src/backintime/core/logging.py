"""Application logging setup."""

import logging
from pathlib import Path


def configure_logging(
    log_file: Path | None = None,
    *,
    level: int = logging.INFO,
) -> logging.Logger:
    """Configure the application logger without adding duplicate handlers."""
    logger = logging.getLogger("backintime")
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file is not None:
        resolved_log_file = log_file.expanduser()
        if not any(
            isinstance(handler, logging.FileHandler)
            and Path(handler.baseFilename) == resolved_log_file.resolve(strict=False)
            for handler in logger.handlers
        ):
            resolved_log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(resolved_log_file, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
            )
            logger.addHandler(file_handler)

    return logger
