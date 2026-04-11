import logging

__all__ = ['setup_logger']

def setup_logger(name):
    '''Create and configure a logger with the given name.

    The logger is set to INFO level and a StreamHandler with a specific
    formatter is added if it does not already have one.
    '''
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
