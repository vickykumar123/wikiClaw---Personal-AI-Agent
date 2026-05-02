"""Utility functions for formatting data."""

import datetime


def format_timestamp(dt: datetime.datetime) -> str:
    """Convert a datetime object to an ISO‑8601 formatted string.

    Args:
        dt: The datetime instance to format.

    Returns:
        An ISO‑8601 formatted string representation of ``dt``.
    """
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, adding an ellipsis if truncated.

    Args:
        text: The original string.
        max_length: The maximum allowed length of the result, including the
            ellipsis when truncation occurs. Defaults to ``100``.

    Returns:
        The original string if its length is less than or equal to ``max_length``;
        otherwise a truncated string ending with an ellipsis character (``…``).
    """
    if len(text) <= max_length:
        return text
    # Reserve space for the ellipsis character.
    if max_length <= 0:
        return "…"
    return text[: max_length - 1] + "…"
