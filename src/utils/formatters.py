"""Utility functions for formatting data."""

import datetime


def format_timestamp(dt: datetime.datetime) -> str:
    """Format a datetime object as an ISO 8601 string.

    Args:
        dt: The datetime object to format.

    Returns:
        A string representation of `dt` in ISO 8601 format.
    """
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, adding ellipsis if truncated.

    Args:
        text: The original string.
        max_length: Maximum allowed length of the returned string. Defaults to
            100.

    Returns:
        The original string if its length is less than or equal to `max_length`;
        otherwise, a truncated string ending with "..." such that the total
        length does not exceed `max_length`.
    """
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        # Not enough space for ellipsis plus characters; return truncated ellipsis.
        return "." * max_length
    return f"{text[: max_length - 3]}..."
