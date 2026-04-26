import logging

def setup_logger(name):
    """Create and configure a logger with the given name.

    The logger is set to INFO level, outputs to the console via a StreamHandler,
    uses the format '[%(asctime)s] %(name)s %(levelname)s: %(message)s',
    and does not propagate to ancestor loggers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger
