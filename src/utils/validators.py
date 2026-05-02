import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Return True if the URL has a valid scheme and netloc."""
    try:
        result = urlparse(url)
        return bool(result.scheme and result.netloc)
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Return True if the email matches a basic pattern."""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.fullmatch(pattern, email) is not None

__all__ = ["validate_url", "validate_email"]