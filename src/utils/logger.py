import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level. If the logger has no handlers,
    a StreamHandler that outputs to the console is attached with a
    simple formatter.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
