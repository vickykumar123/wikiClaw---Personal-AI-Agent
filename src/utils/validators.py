"""Utility validation functions.

Provides simple helpers to validate URLs and email addresses.
"""

import re
from urllib.parse import urlparse
from typing import Pattern


def validate_url(url: str) -> bool:
    """Validate that a string is a well‑formed HTTP or HTTPS URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL has a scheme of ``http`` or ``https`` and a non‑empty
        network location; otherwise ``False``.
    """
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate that a string matches a simple email pattern.

    This uses a basic regular expression that checks for the presence of a
    single ``@`` symbol and at least one ``.`` in the domain part. It is not
    intended to cover all edge cases defined by RFC 5322.

    Args:
        email: The email address to validate.

    Returns:
        True if the email matches the pattern; otherwise ``False``.
    """
    email_regex: Pattern[str] = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    return bool(email_regex.match(email))
