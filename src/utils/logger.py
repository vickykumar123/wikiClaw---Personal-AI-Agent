import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Create (or retrieve) a logger with the given name.

    The logger is configured to log at INFO level and output to the console
    with a formatter that includes the timestamp, logger name, level, and
    the log message.

    If the logger already has handlers attached, they will not be duplicated.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Add a StreamHandler only if one hasn't been added yet
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
