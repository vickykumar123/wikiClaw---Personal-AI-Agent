"""Utility validation functions.

Provides simple validators for URLs and email addresses.
"""

from urllib.parse import urlparse
from email.utils import parseaddr
from typing import List

__all__: List[str] = ["validate_url", "validate_email"]

def validate_url(url: str) -> bool:
    """Validate that the given URL uses HTTP or HTTPS and has a netloc.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL has a scheme of 'http' or 'https' and a non-empty netloc,
        otherwise False.
    """
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Validate an email address format using the standard library.

    Args:
        email: The email address string to validate.

    Returns:
        True if the email address appears to be in a valid format, otherwise False.
    """
    name, addr = parseaddr(email)
    # parseaddr returns an empty string for an invalid address
    if not addr:
        return False
    # Ensure the parsed address matches the original input (no surrounding name part)
    if addr != email:
        return False
    # Basic checks for local part and domain
    if "@" not in addr:
        return False
    local, domain = addr.split("@", 1)
    if not local or not domain:
        return False
    # Domain should contain at least one dot
    if "." not in domain:
        return False
    return True
