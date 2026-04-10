"""Utility functions for formatting."""

import datetime

def format_timestamp(dt: datetime.datetime) -> str:
    """Format a datetime object as a string 'YYYY-MM-DD HH:MM:SS'."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length characters, adding ellipsis if truncated."""
    if len(text) > max_length:
        return text[:max_length - 3] + '...'
    return text
