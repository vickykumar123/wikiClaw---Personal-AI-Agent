"""Utility functions for formatting data."""

from datetime import datetime


def format_timestamp(dt: datetime) -> str:
    """
    Format a datetime object as a string in the format 'YYYY-MM-DD HH:MM:SS'.

    Args:
        dt: The datetime object to format.

    Returns:
        A string representation of the datetime.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate a string to a maximum length, appending '...' if truncation occurs.

    Args:
        text: The string to truncate.
        max_length: The maximum allowed length of the returned string.

    Returns:
        The original string if its length is less than or equal to max_length,
        otherwise a truncated string ending with '...'.
    """
    if len(text) <= max_length:
        return text
    # Subtract length of ellipsis to keep total length within max_length
    truncated = text[: max_length - 3]
    return f"{truncated}..."
