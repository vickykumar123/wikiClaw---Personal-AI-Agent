import logging

def setup_logger(name):
    """
    Set up and return a logger with the given name.
    The logger is configured to log INFO level messages to the console
    with a specific format. If the logger already has a StreamHandler,
    no additional handler is added.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Check if a StreamHandler is already attached
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
