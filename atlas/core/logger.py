"""Logger factory — configure and return a stdlib logger."""

from __future__ import annotations

import logging
import sys


def create_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Create a configured logger with a stream handler.

    Each call returns the *same* logger for a given *name* (stdlib
    behaviour), but only attaches a handler on the first call.

    Args:
        name:  Logger name (typically the application name).
        level: Logging level as an uppercase string.

    Returns:
        A configured :class:`logging.Logger`.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers when called more than once.
    if not logger.handlers:
        logger.setLevel(getattr(logging, level, logging.INFO))

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logger.level)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
