import logging


def setup_logger(name):
    """Create and configure a logger with the given name.

    The logger is set to INFO level and a console StreamHandler is added
    with a specific format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
