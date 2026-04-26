"""Utility validation functions."""

import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Validate that the given URL has a scheme and network location.
    """
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)

def validate_email(email: str) -> bool:
    """
    Simple email validation using a regular expression.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'
    return re.fullmatch(pattern, email) is not None
