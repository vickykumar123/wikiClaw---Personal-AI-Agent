"""Utility module for configuring loggers.

This module provides a helper function to create and configure a logger with a
standard console output format. The logger is set to the INFO level, and a
StreamHandler with a simple formatter is attached.
"""

from __future__ import annotations

import logging
from logging import Logger
from typing import Final

# Define a default log format for console output.
_DEFAULT_FORMAT: Final[str] = (
    "% (asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def setup_logger(name: str) -> Logger:
    """Create and configure a logger.

    The returned logger is configured with:

    * Level set to ``logging.INFO``.
    * A ``StreamHandler`` that writes to ``sys.stderr``.
    * A simple ``Formatter`` that includes timestamp, logger name, level, and
      the log message.

    Args:
        name: The name of the logger, typically ``__name__`` of the module
            requesting the logger.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    logger: Logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if the logger is already configured.
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(_DEFAULT_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
