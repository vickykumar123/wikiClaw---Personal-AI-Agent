# src/utils/formatters.py

"""Utility formatters.

This module provides helper functions for formatting timestamps and truncating text.
"""

import datetime


def format_timestamp(dt: datetime.datetime) -> str:
    """
    Convert a datetime object to an ISO‑8601 formatted string.

    Parameters
    ----------
    dt : datetime.datetime
        The datetime to format.

    Returns
    -------
    str
        ISO‑8601 formatted timestamp.
    """
    if dt.tzinfo is None:
        # Assume naive datetime is in UTC
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate a string to a maximum length, adding an ellipsis if it was truncated.

    Parameters
    ----------
    text : str
        The text to truncate.
    max_length : int, optional
        Maximum allowed length of the returned string (including ellipsis). Default is 100.

    Returns
    -------
    str
        The possibly truncated string.
    """
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        # Not enough room for ellipsis, just cut
        return text[:max_length]
    return text[: max_length - 3] + "..."
