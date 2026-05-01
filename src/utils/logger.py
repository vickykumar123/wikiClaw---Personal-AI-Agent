import logging
from logging import Logger


def setup_logger(name: str) -> Logger:
    """Create and configure a logger.

    Args:
        name: Name of the logger.

    Returns:
        Configured logger instance with a console handler at INFO level.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Add a console handler if none exist to avoid duplicate handlers.
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
