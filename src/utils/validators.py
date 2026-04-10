import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Return True if url is syntactically valid, else False."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Return True if email matches a basic pattern, else False."""
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None
