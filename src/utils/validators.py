"""Utility validation functions."""
import urllib.parse
import re


def validate_url(url: str) -> bool:
    """
    Validate that the given URL has a non-empty scheme and netloc.
    """
    parsed = urllib.parse.urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def validate_email(email: str) -> bool:
    """
    Validate email address using a simple regex.
    """
    pattern = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    return bool(pattern.match(email))
