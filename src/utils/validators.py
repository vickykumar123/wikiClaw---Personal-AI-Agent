from urllib.parse import urlparse
import re

def validate_url(url: str) -> bool:
    """Validate that a URL has a scheme and network location.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL contains a scheme and netloc, otherwise False.

    Raises:
        ValueError: If `url` is not a string.
    """
    if not isinstance(url, str):
        raise ValueError("url must be a string")
    parsed = urlparse(url)
    return bool(parsed.scheme) and bool(parsed.netloc)


def validate_email(email: str) -> bool:
    """Validate basic email format using a regular expression.

    Args:
        email: The email address string to validate.

    Returns:
        True if the email matches the expected pattern, otherwise False.

    Raises:
        ValueError: If `email` is not a string.
    """
    if not isinstance(email, str):
        raise ValueError("email must be a string")
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email) is not None
