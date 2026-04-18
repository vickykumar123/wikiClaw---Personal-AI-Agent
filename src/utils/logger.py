import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level and has a StreamHandler with a
    formatter that outputs timestamps, the logger name, level, and message.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if the logger is already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
