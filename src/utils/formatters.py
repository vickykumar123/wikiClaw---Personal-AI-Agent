"""Utility functions for formatting timestamps and text."""

from datetime import datetime
from typing import Union

def format_timestamp(dt: Union[datetime, str]) -> str:
    """
    Format a datetime object or string to 'YYYY-MM-DD HH:MM:SS'.

    If `dt` is a string, it will be parsed using `datetime.fromisoformat`.
    """
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Return the original text if its length is <= max_length,
    otherwise return the first max_length characters followed by an ellipsis.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
