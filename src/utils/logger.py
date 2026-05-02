# src/utils/logger.py
"""Utility module for configuring application loggers.

Provides a helper function to create a logger with a predefined INFO level
and a simple console ``StreamHandler``. The handler is added only once to
prevent duplicate log entries when the function is called multiple times
for the same logger name.
"""

import logging
from logging import Logger


def setup_logger(name: str) -> Logger:
    """Create or retrieve a logger configured for console output.

    The logger is set to ``INFO`` level. If the logger does not already have
    any handlers attached, a :class:`logging.StreamHandler` with a basic
    formatter is added. Subsequent calls with the same ``name`` will return the
    existing logger without adding additional handlers.

    Args:
        name: The name of the logger to configure.

    Returns:
        The configured :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
