import datetime


def format_timestamp(dt: datetime.datetime) -> str:
    """Format a datetime object as 'YYYY-MM-DD HH:MM:SS'."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate *text* to *max_length* characters, appending '...' if truncated.

    Args:
        text: The string to potentially truncate.
        max_length: Maximum number of characters to keep before adding ellipsis.
    """
    if len(text) > max_length:
        return text[:max_length] + '...'
    return text
