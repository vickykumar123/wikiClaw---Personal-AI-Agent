"""Utility functions for formatting."""

from datetime import datetime

def format_timestamp(dt: datetime) -> str:
    """
    Convert a datetime object to a string in the format 'YYYY-MM-DD HH:MM:SS'.

    Args:
        dt: A datetime object to format.

    Returns:
        A string representing the formatted datetime.
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate a string to a maximum length, adding an ellipsis if it was truncated.

    Args:
        text: The string to potentially truncate.
        max_length: The maximum allowed length of the string before truncation.

    Returns:
        The original string if its length is within the limit, otherwise a truncated
        version ending with '...'.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'
