"""
QShield Enterprise
==================

Central logging configuration.

All modules should use:

    from app.core.logging import get_logger

    logger = get_logger(__name__)

Do NOT use print() anywhere in the application.

The logger writes to both:

- Console
- Rotating log file

This file should contain NO business logic.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.settings import settings

# ---------------------------------------------------------------------
# Internal State
# ---------------------------------------------------------------------

_LOGGING_INITIALIZED = False


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for development.

    File logging remains plain text.
    """

    RESET = "\033[0m"

    COLORS = {
        logging.DEBUG: "\033[36m",      # Cyan
        logging.INFO: "\033[32m",       # Green
        logging.WARNING: "\033[33m",    # Yellow
        logging.ERROR: "\033[31m",      # Red
        logging.CRITICAL: "\033[41m",   # Red Background
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.RESET)

        formatted = super().format(record)

        return f"{color}{formatted}{self.RESET}"


def _build_console_handler() -> logging.Handler:
    """
    Creates the console logger.
    """

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(
        ColoredFormatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    return handler


def _build_file_handler() -> logging.Handler:
    """
    Creates the rotating file logger.
    """

    log_path: Path = settings.log_file

    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=10 * 1024 * 1024,   # 10 MB
        backupCount=10,
        encoding="utf-8",
    )

    handler.setFormatter(
        logging.Formatter(
            fmt=(
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(filename)s:%(lineno)d | "
                "%(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    return handler


def configure_logging() -> None:
    """
    Configures application logging.

    Safe to call multiple times.
    """

    global _LOGGING_INITIALIZED

    if _LOGGING_INITIALIZED:
        return

    root_logger = logging.getLogger()

    root_logger.setLevel(settings.log_level.upper())

    # Prevent duplicate handlers if uvicorn reloads
    root_logger.handlers.clear()

    root_logger.addHandler(_build_console_handler())
    root_logger.addHandler(_build_file_handler())

    # Reduce noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    _LOGGING_INITIALIZED = True

    logger = logging.getLogger("qshield")

    logger.info("=" * 70)
    logger.info("%s %s", settings.app_name, settings.app_version)
    logger.info("Logging initialized")
    logger.info("Log file : %s", settings.log_file)
    logger.info("Log level: %s", settings.log_level)
    logger.info("=" * 70)


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger.

    Example
    -------
        logger = get_logger(__name__)
    """

    configure_logging()

    return logging.getLogger(name)