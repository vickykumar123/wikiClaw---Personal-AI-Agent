import logging
from logging import Logger, StreamHandler, Formatter


def setup_logger(name: str) -> Logger:
    """Create and configure a logger.

    Args:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger with INFO level and a stream
        handler using a simple formatter.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
