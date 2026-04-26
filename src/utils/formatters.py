"""Utility functions for formatting values used across the project.

This module provides helpers to format timestamps and truncate long text
strings in a consistent manner.
"""

import datetime
from typing import Any


def format_timestamp(dt: datetime.datetime) -> str:
    """Convert a :class:`datetime.datetime` to an ISO‑8601 string.

    Args:
        dt: The datetime object to format.

    Returns:
        An ISO‑8601 formatted string representation of ``dt``.
    """
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate ``text`` to ``max_length`` characters, appending an ellipsis.

    If the length of ``text`` exceeds ``max_length``, the function returns the
    first ``max_length`` characters followed by ``'...'``. Otherwise, the
    original ``text`` is returned unchanged.

    Args:
        text: The string to potentially truncate.
        max_length: Maximum number of characters to retain before adding the
            ellipsis. Defaults to 100.

    Returns:
        The possibly truncated string.
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
