"""Utility for configuring loggers used across the project.

Provides a helper function to obtain a pre-configured logger
with a consistent format and INFO level.
"""

import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """
    Obtain a logger with the given *name*, configure it to log at INFO level,
    and attach a StreamHandler to stdout with a standard formatter if it has
    no handlers attached.

    Parameters
    ----------
    name : str
        Name of the logger to retrieve.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
