import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level and has a console ``StreamHandler`` with a
    formatter that outputs timestamps, the logger name, the log level and the
    message.  The handler is added only once to avoid duplicate log entries.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Define formatter
    formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")

    # Add a console handler if not already present
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
