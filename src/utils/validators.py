"""Utility validation functions."""

import re
from urllib.parse import urlparse

__all__ = ["validate_url", "validate_email"]

def validate_url(url: str) -> bool:
    """Return True if *url* parses to a URL with a non‑empty scheme and netloc."""
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)

def validate_email(email: str) -> bool:
    """Return True if *email* matches a basic email pattern."""
    if not isinstance(email, str):
        return False
    # Simple email regex: one or more word chars, dots, plus, hyphen before @,
    # then domain part with at least one dot.
    pattern = r"^[\w\.\+\-]+@[\w\.\-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(pattern, email) is not None
