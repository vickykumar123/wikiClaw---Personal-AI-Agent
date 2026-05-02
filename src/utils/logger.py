import logging

def setup_logger(name):
    """
    Create or retrieve a logger with the given name.
    Configures the logger to log INFO level messages to the console with a
    specific format. Duplicate handlers are avoided.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate console handlers
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
