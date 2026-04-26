import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate that the given string is a well-formed URL.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate a basic email address using regex.
    """
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
    return re.match(pattern, email) is not None
