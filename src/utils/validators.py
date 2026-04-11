"""Utility validators for URLs and email addresses."""

import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Return True if *url* is syntactically a valid URL.

    A URL is considered valid when ``urlparse`` yields a non‑empty scheme
    and netloc.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """
    Return True if *email* matches a basic email pattern.

    The pattern checks for a local part, an ``@`` symbol, and a domain
    with at least one dot. It does not guarantee the address exists.
    """
    pattern = re.compile(
        r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    )
    return bool(pattern.match(email))
