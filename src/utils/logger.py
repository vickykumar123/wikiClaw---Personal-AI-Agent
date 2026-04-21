import logging
import sys


def setup_logger(name):
    """Create and configure a logger with a StreamHandler to stdout.

    The logger is set to INFO level and uses the format:
    '[%(asctime)s] %(name)s %(levelname)s: %(message)s'.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Add handler only if the logger doesn't have one already
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
