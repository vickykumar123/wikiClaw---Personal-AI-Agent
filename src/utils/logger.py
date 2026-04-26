"""Utility for configuring loggers."""

import logging
from logging import Logger, StreamHandler, Formatter


def setup_logger(name: str) -> Logger:
    """Create and configure a logger.

    Args:
        name: The name of the logger.

    Returns:
        Configured ``logging.Logger`` instance with INFO level and a
        ``StreamHandler`` using a simple formatter. Duplicate handlers are
        avoided if the logger has already been configured.
    """
    logger: Logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Add a StreamHandler only if one hasn't been added already.
    if not any(isinstance(h, StreamHandler) for h in logger.handlers):
        handler: StreamHandler = StreamHandler()
        formatter: Formatter = Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
