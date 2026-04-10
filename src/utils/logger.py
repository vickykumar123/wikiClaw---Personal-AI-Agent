import logging

__all__ = ["setup_logger"]

def setup_logger(name):
    """
    Create and configure a logger with the given name.

    The logger is set to INFO level and has a StreamHandler with a formatter:
    "[%(asctime)s] %(name)s %(levelname)s: %(message)s"
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if logger already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
