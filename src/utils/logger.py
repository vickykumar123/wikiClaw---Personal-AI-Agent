import logging
from src.constants import LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger(name: str) -> logging.Logger:
    """Create and configure a logger.

    Args:
        name: Name for the logger.

    Returns:
        Configured logger instance with INFO level and a stream handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
