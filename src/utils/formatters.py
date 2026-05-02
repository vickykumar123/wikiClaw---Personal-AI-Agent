"""Utility functions for formatting data.

This module provides helpers to format timestamps and truncate long text strings.
"""

from datetime import datetime
from typing import Any

__all__ = ["format_timestamp", "truncate_text"]


def format_timestamp(dt: datetime) -> str:
    """Return a string representation of *dt* in ``YYYY-MM-DD HH:MM:SS`` format.

    Args:
        dt: A :class:`datetime.datetime` instance.

    Returns:
        A formatted timestamp string.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate *text* to *max_length* characters, appending ``...`` if truncated.

    Args:
        text: The original string.
        max_length: Maximum length of the returned string **before** adding the
            ellipsis. Defaults to ``100``.

    Returns:
        The possibly truncated string.
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
