"""Utility functions for formatting."""

from datetime import datetime

def format_timestamp(dt: datetime) -> str:
    """Return a timestamp string in 'YYYY-MM-DD HH:MM:SS' format."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length characters, appending '...' if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'