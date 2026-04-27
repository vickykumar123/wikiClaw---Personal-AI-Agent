import logging


def setup_logger(name):
    """Create and configure a logger with the given *name*.

    The logger is set to INFO level and a single ``StreamHandler`` is
    attached with the format ``[%(asctime)s] %(name)s %(levelname)s: %(message)s``.
    The handler is added only once even if ``setup_logger`` is called multiple
    times for the same logger name.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Add a StreamHandler only if the logger doesn't have one already.
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
