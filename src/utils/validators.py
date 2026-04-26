"""Utility validators for URLs and email addresses."""

import urllib.parse
import re

def validate_url(url: str) -> bool:
    """
    Validate that the given URL has a scheme of 'http' or 'https' and a non-empty netloc.
    Returns True if valid, False otherwise.
    """
    try:
        result = urllib.parse.urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """
    Validate email address using a simple regular expression.
    Returns True if the email matches the pattern, False otherwise.
    """
    # Simple regex for basic email validation
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None