import datetime
from typing import Any


def format_timestamp(dt: datetime.datetime) -> str:
    """Return a string representation of a datetime.

    The format used is ``'YYYY-MM-DD HH:MM:SS'``.

    Args:
        dt: The datetime instance to format.

    Returns:
        A formatted datetime string.
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, appending an ellipsis if needed.

    If the original string exceeds ``max_length``, it will be cut down to
    ``max_length - 3`` characters and ``'...'`` will be appended, ensuring the
    final result does not exceed ``max_length``.

    Args:
        text: The string to truncate.
        max_length: The maximum allowed length of the result. Defaults to 100.

    Returns:
        The possibly truncated string.
    """
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return '.' * max_length
    return text[: max_length - 3] + '...'
