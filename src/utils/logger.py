import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level and has a console StreamHandler with a
    formatter that outputs timestamps, logger name, level, and the message.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # If logger already has handlers, avoid adding duplicate handlers
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
