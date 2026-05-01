import re
from urllib.parse import urlparse
from typing import Final

__all__: Final = [
    "validate_url",
    "validate_email",
    "validate_port",
]

def validate_url(url: str) -> bool:
    """Validate a URL string.

    This function checks whether the provided ``url`` has a valid scheme and network
    location using :mod:`urllib.parse`. It returns ``True`` if the URL appears to be
    well‑formed, otherwise ``False``.

    Args:
        url: The URL to validate.

    Returns:
        ``True`` if ``url`` has a non‑empty scheme and netloc, ``False`` otherwise.

    Raises:
        ValueError: If ``url`` is not a string or is an empty string.
    """
    if not isinstance(url, str):
        raise ValueError("URL must be a string.")
    if not url:
        raise ValueError("URL cannot be empty.")

    parsed = urlparse(url)
    # A valid URL should have at least scheme (e.g., http, https) and netloc (domain)
    return bool(parsed.scheme) and bool(parsed.netloc)

def validate_email(email: str) -> bool:
    """Validate an email address using a regular expression.

    The function applies a simple yet robust regular expression that matches most
    common email address formats. It returns ``True`` for a syntactically valid
    email and ``False`` otherwise.

    Args:
        email: The email address to validate.

    Returns:
        ``True`` if ``email`` matches the pattern, ``False`` otherwise.

    Raises:
        ValueError: If ``email`` is not a string or is an empty string.
    """
    if not isinstance(email, str):
        raise ValueError("Email must be a string.")
    if not email:
        raise ValueError("Email cannot be empty.")

    email_regex = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    )
    return bool(email_regex.fullmatch(email))


def validate_port(port: int) -> bool:
    """Validate that a port number is within the valid range.

    Args:
        port: The port number to validate.

    Returns:
        True if ``port`` is an integer between 1 and 65535, otherwise False.

    Raises:
        ValueError: If ``port`` is not an integer.
    """
    if not isinstance(port, int):
        raise ValueError("Port must be an integer.")
    return 1 <= port <= 65535
