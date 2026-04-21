"""Utility validators for URL and email."""

import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate a URL string.

    Returns True if the URL has a scheme and netloc (e.g., ``http://example.com``).
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc)
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """
    Validate an email address using a regular expression.

    Returns True if the email matches a basic pattern.
    """
    email_pattern = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
    )
    return bool(email_pattern.fullmatch(email))


__all__ = ["validate_url", "validate_email"]