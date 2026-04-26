import datetime

__all__ = ["format_timestamp", "truncate_text"]

def format_timestamp(dt: datetime.datetime) -> str:
    """Format a datetime object as an ISO 8601 string.

    Args:
        dt: The datetime instance to format.

    Returns:
        The ISO 8601 formatted string representation of ``dt``.
    """
    return dt.isoformat()

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, adding an ellipsis if truncated.

    Args:
        text: The original string to potentially truncate.
        max_length: The maximum allowed length of the returned string. Defaults to 100.

    Returns:
        The original string if its length is less than or equal to ``max_length``;
        otherwise, a truncated version ending with ``...``.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."
