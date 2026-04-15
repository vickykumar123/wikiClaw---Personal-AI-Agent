import logging


def setup_logger(name):
    '''
    Create and configure a logger with the given name.

    The logger is set to INFO level and outputs to the console with a
    formatter that includes the timestamp, logger name, level, and message.
    '''
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create console handler with the specified format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)

    # Avoid adding multiple handlers if the logger already has handlers
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger
