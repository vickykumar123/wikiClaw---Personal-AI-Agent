import logging


def setup_logger(name: str) -> logging.Logger:
    """Create and configure a logger with the given name.

    The logger is set to INFO level and a ``StreamHandler`` is added with a
    formatter that outputs messages in the form::

        [%(asctime)s] %(name)s %(levelname)s: %(message)s

    If the logger already has handlers attached, they are left unchanged to
    avoid adding duplicate handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
