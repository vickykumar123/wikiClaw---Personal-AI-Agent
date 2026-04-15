import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the specified name.

    The logger is set to INFO level and has a console StreamHandler with a
    simple formatter.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create console handler if not already added
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
