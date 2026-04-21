import logging

def setup_logger(name):
    """
    Set up a logger with the given name.

    The logger is configured to log at INFO level and outputs to the console
    with a formatter that includes the timestamp, logger name, log level,
    and message.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
