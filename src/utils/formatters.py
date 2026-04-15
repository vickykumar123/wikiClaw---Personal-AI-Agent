"""Utility functions for formatting."""

from datetime import datetime
from typing import AnyStr

def format_timestamp(dt: datetime) -> str:
    """
    Format a datetime object as a string 'YYYY-MM-DD HH:MM:SS'.

    Args:
        dt: The datetime object to format.

    Returns:
        A formatted timestamp string.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: AnyStr, max_length: int = 100) -> AnyStr:
    """
    Truncate a string to a maximum length, adding an ellipsis if truncated.

    Args:
        text: The text to potentially truncate.
        max_length: Maximum allowed length of the returned string.

    Returns:
        The original text if its length is within max_length,
        otherwise a truncated version ending with '...'.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
