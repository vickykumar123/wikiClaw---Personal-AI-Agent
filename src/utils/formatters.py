"""Utility functions for formatting."""

import datetime


def format_timestamp(dt: datetime.datetime) -> str:
    """Convert a datetime object to an ISO‑8601 formatted string.

    Args:
        dt: The datetime instance to format.

    Returns:
        An ISO‑8601 string representation of ``dt``.
    """
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, adding an ellipsis if needed.

    If ``text`` exceeds ``max_length``, it will be shortened to fit within the
    limit and an ellipsis (``...``) will be appended.

    Args:
        text: The string to potentially truncate.
        max_length: The maximum allowed length of the returned string. Defaults
            to ``100``. Must be at least ``3`` to accommodate the ellipsis.

    Returns:
        The original ``text`` if its length is within ``max_length``; otherwise
        a truncated version ending with ``...``.
    """
    if max_length < 3:
        # Not enough room for an ellipsis; just cut the string.
        return text[:max_length]

    if len(text) > max_length:
        return text[: max_length - 3] + "..."
    return text
