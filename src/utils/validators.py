"""Utility validators for URLs and email addresses.

This module provides simple validation functions for URLs and email addresses
using regular expressions.
"""

import re


def validate_url(url: str) -> bool:
    """Return ``True`` if *url* matches a basic HTTP/HTTPS URL pattern.

    The pattern checks for an ``http`` or ``https`` scheme, a domain name, an
    optional port, and an optional path.
    """
    pattern = re.compile(
        r"^(https?://)"          # scheme
        r"([A-Za-z0-9.-]+)"      # domain
        r"(:\d+)?"              # optional port
        r"(/.*)?$"               # optional path
    )
    return bool(pattern.match(url))


def validate_email(email: str) -> bool:
    """Return ``True`` if *email* matches a typical email address pattern.

    The pattern allows alphanumeric characters and a set of common symbols in the
    local part, followed by an ``@`` and a domain with a top‑level domain of at
    least two characters.
    """
    pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    return bool(pattern.match(email))
