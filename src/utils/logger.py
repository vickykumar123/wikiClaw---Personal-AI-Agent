import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level and has a console StreamHandler with a
    formatter that outputs messages in the form:
    '[%(asctime)s] %(name)s %(levelname)s: %(message)s'.

    Duplicate handlers are avoided.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Define formatter
    formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')

    # Add a console handler if not already present
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
