"""Utility formatters module."""

from datetime import datetime


def format_timestamp(dt: datetime) -> str:
    """Format a datetime object as 'YYYY-MM-DD HH:MM:SS'.

    Args:
        dt (datetime): The datetime to format.

    Returns:
        str: Formatted timestamp string.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, adding ellipsis if truncated.

    Args:
        text (str): The input string.
        max_length (int, optional): Maximum allowed length. Defaults to 100.

    Returns:
        str: Possibly truncated string.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."
