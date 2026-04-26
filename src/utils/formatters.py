'''Utility functions for formatting.'''

import datetime
from typing import Any


def format_timestamp(dt: datetime.datetime) -> str:
    """Format a datetime object as an ISO 8601 string.

    Args:
        dt: The datetime object to format.

    Returns:
        An ISO 8601 formatted string representation of ``dt``.
    """
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, appending an ellipsis if truncated.

    Args:
        text: The string to truncate.
        max_length: The maximum allowed length of the returned string, including
            the ellipsis if truncation occurs. Defaults to ``100``.

    Returns:
        The possibly truncated string. If ``text`` exceeds ``max_length``,
        it is cut off at ``max_length - 3`` characters and ``...`` is appended.
    """
    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return "." * max_length
    return text[: max_length - 3] + "..."
