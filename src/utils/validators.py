# Utility validators for URLs and email addresses.

import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """Validate that a URL has a scheme and network location.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL contains both a scheme (e.g., ``http`` or ``https``) and a netloc,
        otherwise False.
    """
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


def validate_email(email: str) -> bool:
    """Validate an email address using a regular expression.

    Args:
        email: The email address to validate.

    Returns:
        True if the email matches the pattern, otherwise False.
    """
    email_regex = re.compile(
        r"(^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$)"
    )
    return bool(email_regex.match(email))
