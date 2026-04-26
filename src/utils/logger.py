"""Utility module for configuring loggers."""

import logging

def setup_logger(name: str) -> logging.Logger:
    """Create and configure a logger with a stream handler.

    Args:
        name: The name of the logger.

    Returns:
        Configured ``logging.Logger`` instance with INFO level and a simple
        stream handler. Duplicate handlers are avoided.
    """
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter: logging.Formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler: logging.StreamHandler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
