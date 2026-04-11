"""Utility validation functions."""

import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Validate that the given string is a syntactically valid URL.

    The function parses the URL using :func:`urllib.parse.urlparse` and
    checks that both the scheme (e.g., ``http`` or ``https``) and the network
    location part (netloc) are present.

    Parameters
    ----------
    url: str
        The URL string to validate.

    Returns
    -------
    bool
        ``True`` if the URL has a non‑empty scheme and netloc, otherwise ``False``.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email(email: str) -> bool:
    """
    Validate that the given string looks like an email address.

    This uses a simple regular expression that checks for the presence of a
    single ``@`` symbol and at least one ``.`` in the domain part. It is not a
    full RFC‑5322 validation but works for most common cases.

    Parameters
    ----------
    email: str
        The email address to validate.

    Returns
    -------
    bool
        ``True`` if the string matches the basic email pattern, otherwise ``False``.
    """
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None
