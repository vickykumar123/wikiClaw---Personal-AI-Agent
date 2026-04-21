'''Utility functions for validation.'''

import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Validate a URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL has both scheme and netloc, otherwise False.
    """
    try:
        result = urlparse(url)
        return bool(result.scheme) and bool(result.netloc)
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """Validate an email address using a simple regular expression.

    Args:
        email: The email address string to validate.

    Returns:
        True if the email matches a basic pattern, otherwise False.
    """
    pattern = r'^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'
    return re.match(pattern, email) is not None