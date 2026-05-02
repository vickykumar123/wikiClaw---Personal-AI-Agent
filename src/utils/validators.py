"""Utility validation functions.

This module provides simple validation helpers for URLs and email addresses.
"""

import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate that a URL is syntactically correct.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL has a valid scheme and network location, otherwise False.
    """
    try:
        result = urlparse(url)
        return bool(result.scheme and result.netloc)
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate that an email address matches a basic pattern.

    Args:
        email: The email address to validate.

    Returns:
        True if the email matches the pattern, otherwise False.
    """
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.fullmatch(pattern, email) is not None
