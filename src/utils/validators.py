import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Validate that the given URL has a scheme and network location.

    Returns True if both are present, otherwise False.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """
    Validate a basic email address format using a regular expression.

    Returns True if the email matches the pattern, otherwise False.
    """
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None
