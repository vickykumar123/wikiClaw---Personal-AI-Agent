"""Utility validation functions."""

import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Return True if `url` is a valid URL with a scheme and netloc.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """
    Return True if `email` matches a basic email pattern.
    """
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None
