import logging

def setup_logger(name):
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level and outputs to the console with a
    formatter that includes the timestamp, logger name, level, and message.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # If the logger already has handlers, avoid adding duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
