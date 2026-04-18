import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level and a StreamHandler with a specific
    formatter is attached. Duplicate handlers are avoided.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Define formatter
    formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')

    # Add a StreamHandler if one hasn't been added already
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
