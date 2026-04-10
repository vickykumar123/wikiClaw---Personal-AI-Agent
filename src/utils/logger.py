import logging

def setup_logger(name):
    """
    Set up and return a logger with the given name.
    The logger is configured to log INFO level messages to the console
    with a specific format. Handlers are added only once.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
