"""Utility validation functions."""

import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate a URL by checking that it has a scheme and network location.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL has both a scheme and netloc, otherwise False.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """
    Validate an email address using a simple regular expression.

    Args:
        email: The email address to validate.

    Returns:
        True if the email matches the pattern, otherwise False.
    """
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None
