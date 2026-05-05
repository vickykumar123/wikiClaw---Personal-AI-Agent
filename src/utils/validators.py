"""Utility validators for URLs and email addresses."""

import re
from typing import Pattern

# Regular expression patterns compiled for performance
_URL_PATTERN: Pattern[str] = re.compile(
    r'^(?:http|https|ftp)://'                     # scheme
    r'(?:\S+(?::\S*)?@)?'                         # optional user:pass@
    r'(?:'                                        # IP address exclusion
    r'(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])'   # 1-223
    r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}'
    r'(?:\.(?:[0-9]{1,3}))'
    r')|'
    r'(?:(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})'       # domain name
    r')'
    r'(?::\d{2,5})?'                              # optional port
    r'(?:[/?#][^\s]*)?'                           # resource path
    r'$',
    re.IGNORECASE,
)

_EMAIL_PATTERN: Pattern[str] = re.compile(
    r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)


def validate_url(url: str) -> bool:
    """Validate a URL string.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL matches a standard pattern, False otherwise.
    """
    return bool(_URL_PATTERN.match(url))


def validate_email(email: str) -> bool:
    """Validate an email address.

    Args:
        email: The email address to validate.

    Returns:
        True if the email matches a standard pattern, False otherwise.
    """
    return bool(_EMAIL_PATTERN.match(email))
