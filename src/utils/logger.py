import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level and, if it has no handlers,
    a StreamHandler with a simple formatter is added.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
