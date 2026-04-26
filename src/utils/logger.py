import logging
from typing import Final


def setup_logger(name: str) -> logging.Logger:
    """Create and configure a logger.

    This function returns a logger with the given *name*, sets its level to
    ``INFO`` and attaches a single :class:`logging.StreamHandler` with a standard
    formatter. If the logger already has a ``StreamHandler`` attached, the
    function will not add another one, preventing duplicate log messages.

    Args:
        name: The name of the logger to create or retrieve.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Ensure only one StreamHandler is attached to avoid duplicate logs.
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler: logging.StreamHandler = logging.StreamHandler()
        formatter: logging.Formatter = logging.Formatter(
            "% (asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
