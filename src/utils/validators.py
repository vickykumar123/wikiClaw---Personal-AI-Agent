import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validate that the given URL has a non-empty scheme and netloc.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL is valid, False otherwise.
    """
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def validate_email(email: str) -> bool:
    """
    Validate that the given email address matches a basic email pattern.

    Args:
        email: The email address string to validate.

    Returns:
        True if the email matches the pattern, False otherwise.
    """
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None
