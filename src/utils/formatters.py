"""Utility functions for formatting."""

from datetime import datetime

def format_timestamp(dt: datetime) -> str:
    """Format a datetime object as 'YYYY-MM-DD HH:MM:SS'."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length, adding ellipsis if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'
