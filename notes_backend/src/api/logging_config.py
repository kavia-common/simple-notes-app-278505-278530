"""Centralized logging configuration for the FastAPI application.

This module configures a structured logger with a log level controlled by
the environment variable REACT_APP_LOG_LEVEL (default: INFO). It ensures
consistent logging across all layers (routers, services, repositories).
"""

from __future__ import annotations

import logging
import os
from typing import Optional


def _parse_log_level(level: Optional[str]) -> int:
    """Parse string log level to logging constant safely."""
    if not level:
        return logging.INFO
    normalized = str(level).strip().upper()
    mapping = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET,
    }
    return mapping.get(normalized, logging.INFO)


# PUBLIC_INTERFACE
def configure_logging() -> None:
    """Configure root logging handlers and levels based on env.

    Env:
        REACT_APP_LOG_LEVEL: str, optional - DEBUG|INFO|WARNING|ERROR|CRITICAL

    Idempotent: safe to call multiple times.
    """
    level = _parse_log_level(os.getenv("REACT_APP_LOG_LEVEL", "INFO"))

    # Prevent duplicate handlers if called multiple times (e.g., in reload)
    root_logger = logging.getLogger()
    if root_logger.handlers:
        # Update levels on existing handlers and root logger
        root_logger.setLevel(level)
        for h in root_logger.handlers:
            h.setLevel(level)
        return

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(stream_handler)
