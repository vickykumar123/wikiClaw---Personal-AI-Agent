"""
Utility validation functions.
"""

import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Validate that the given string is a well-formed URL.

    This function parses the URL using :func:`urllib.parse.urlparse` and
    checks that it has at least a scheme and netloc component.

    Args:
        url: The URL string to validate.

    Returns:
        True if ``url`` appears to be a valid URL, otherwise False.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """
    Validate that the given string looks like an email address.

    A simple regular expression is used to check for the pattern
    ``<local-part>@<domain>``. It does not guarantee that the address exists,
    only that it conforms to a typical email format.

    Args:
        email: The email address string to validate.

    Returns:
        True if ``email`` matches the pattern, otherwise False.
    """
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.fullmatch(pattern, email) is not None