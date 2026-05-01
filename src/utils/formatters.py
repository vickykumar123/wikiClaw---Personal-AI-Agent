import datetime
from typing import Any

__all__: list[str] = ["format_timestamp", "truncate_text"]

def format_timestamp(dt: datetime.datetime) -> str:
    """Formats a :class:`datetime.datetime` object as an ISO‑8601 string.

    Args:
        dt: The datetime instance to format.

    Returns:
        A string representation of ``dt`` in ISO‑8601 format. If ``dt`` is
        timezone‑aware, the offset is included; otherwise the result is naive.
    """
    return dt.isoformat()

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncates a string to a maximum length, adding an ellipsis if needed.

    If *text* exceeds *max_length*, it is cut short and an ellipsis (``...``)
    is appended. The total length of the returned string will not exceed
    ``max_length`` when an ellipsis is added.

    Args:
        text: The original string.
        max_length: Maximum allowed length of the returned string. Must be
            at least 3; otherwise, a :class:`ValueError` is raised.

    Returns:
        The possibly‑truncated string.
    """
    if max_length < 3:
        raise ValueError("max_length must be at least 3 to accommodate ellipsis.")
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
