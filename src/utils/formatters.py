"""Utility functions for formatting."""

from datetime import datetime


def format_timestamp(dt: datetime) -> str:
    """Format a datetime object as 'YYYY-MM-DD HH:MM:SS'."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate the string to `max_length` characters, appending '...' if truncation occurs."""
    if len(text) > max_length:
        return text[:max_length] + '...'
    return text


__all__ = [
    'format_timestamp',
    'truncate_text',
]
