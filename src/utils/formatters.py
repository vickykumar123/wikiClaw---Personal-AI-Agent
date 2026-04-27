"""Utility functions for formatting."""

import datetime


def format_timestamp(dt: datetime.datetime) -> str:
    """Return the given datetime formatted as 'YYYY-MM-DD HH:MM:SS'.

    Args:
        dt: The datetime object to format.

    Returns:
        A string representation of the datetime in the format
        ``YYYY-MM-DD HH:MM:SS``.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, appending '...' if it was truncated.

    Args:
        text: The string to truncate.
        max_length: The maximum allowed length of the returned string,
            including the ellipsis if truncation occurs.

    Returns:
        The possibly truncated string.
    """
    if len(text) > max_length:
        # Ensure the ellipsis fits within max_length
        return text[: max_length - 3] + "..."
    return text
