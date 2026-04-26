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

def validate_port(port: int) -> bool:
    """Validate that a port number is within the valid range (0-65535).

    Args:
        port: The port number to validate.

    Returns:
        True if ``port`` is an integer between 0 and 65535 inclusive;
        otherwise ``False``.
    """
    return isinstance(port, int) and 0 <= port <= 65535

def validate_phone(phone: str) -> None:
    """Validate that a phone number matches common patterns.

    The function checks for an optional leading ``+`` followed by digits,
    allowing spaces, dashes ``-`` or parentheses ``()`` as separators.
    It raises a ``ValueError`` if the input does not conform to the pattern.

    Args:
        phone: The phone number string to validate.

    Raises:
        ValueError: If ``phone`` does not match the expected format.

    Examples:
        >>> validate_phone("+1 (555) 123-4567")
        >>> validate_phone("5551234567")
        >>> validate_phone("invalid")
        Traceback (most recent call last):
            ...
        ValueError: Invalid phone number format: invalid
    """
    phone_regex: Pattern[str] = re.compile(
        r'^\+?\d[\d\s\-\(\)]*$'
    )
    if not phone_regex.fullmatch(phone):
        raise ValueError(f"Invalid phone number format: {phone}")
