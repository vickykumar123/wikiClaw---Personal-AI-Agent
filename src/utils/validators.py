"""Utility validation functions."""

from urllib.parse import urlparse
import re

__all__ = ["validate_url", "validate_email"]

def validate_url(url: str) -> bool:
    """Return True if the given string is a syntactically valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Return True if the given string matches a basic email pattern."""
    pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    return bool(pattern.match(email))
