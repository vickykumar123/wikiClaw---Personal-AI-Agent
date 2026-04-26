"""Utility validation functions."""

from urllib.parse import urlparse
import re


def validate_url(url: str) -> bool:
    """Validates that a given string is a well‑formed URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL has a valid scheme (http or https) and network location,
        False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validates that a given string looks like a valid email address.

    A simple regular expression is used for validation; it checks for the presence
    of exactly one ``@`` symbol and at least one ``.`` in the domain part.

    Args:
        email: The email address string to validate.

    Returns:
        True if the email matches the pattern, False otherwise.
    """
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None
