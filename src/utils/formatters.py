"""Utility functions for formatting data."""
from datetime import datetime


def format_timestamp(dt: datetime) -> str:
    """Format a datetime object as an ISO‑8601 string.

    Args:
        dt: The datetime instance to format.

    Returns:
        A string representation of ``dt`` in ISO‑8601 format.
    """
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, adding an ellipsis if needed.

    Args:
        text: The text to truncate.
        max_length: The maximum allowed length of the returned string. Defaults
            to ``100`` characters.

    Returns:
        The original ``text`` if its length is less than or equal to
        ``max_length``; otherwise a truncated version ending with ``...``.
    """
    if len(text) <= max_length:
        return text
    ellipsis = "..."
    truncated = text[: max_length - len(ellipsis)]
    return f"{truncated}{ellipsis}"
