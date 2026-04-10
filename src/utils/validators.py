"""Utility validators for URL and email.

Provides simple regular expression based validation functions.
"""

import re

__all__ = ["validate_url", "validate_email"]

def validate_url(url: str) -> bool:
    """Return True if *url* matches a basic URL pattern, else False."""
    pattern = re.compile(
        r'^(https?://)?'          # optional scheme
        r'([\da-z.-]+)\.'       # subdomain/domain
        r'([a-z.]{2,6})'          # top-level domain
        r'([/\w .-]*)*/?$'       # optional path
    , re.IGNORECASE)
    return bool(pattern.match(url))

def validate_email(email: str) -> bool:
    """Return True if *email* matches a basic email pattern, else False."""
    pattern = re.compile(
        r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
    )
    return bool(pattern.match(email))
