import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Return True if the given string looks like a valid URL.
    This is a basic check that ensures the scheme and netloc are present.
    """
    if not isinstance(url, str):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """
    Return True if the given string looks like a valid email address.
    This uses a simple regular expression for basic validation.
    """
    if not isinstance(email, str):
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.fullmatch(pattern, email) is not None
