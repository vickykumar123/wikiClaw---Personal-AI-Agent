"""Utility validators for URLs and email addresses."""

import re

# Regular expression for a simple URL validation
URL_REGEX = re.compile(
    r'^(https?://)?'                     # optional scheme
    r'([A-Za-z0-9.-]+)'                  # domain
    r'(\\.[A-Za-z]{2,})'                 # top-level domain
    r'(:\\d+)?'                          # optional port
    r'(/.*)?'                            # optional path
)

# Regular expression for a basic email validation
EMAIL_REGEX = re.compile(
    r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
)

def validate_url(url: str) -> bool:
    """Validate that *url* conforms to a basic URL format.

    The check is performed using a regular expression that supports optional
    ``http``/``https`` scheme, domain name, optional port, and optional path.

    Parameters
    ----------
    url: str
        The URL string to validate.

    Returns
    -------
    bool
        ``True`` if *url* matches the pattern, otherwise ``False``.
    """
    return bool(URL_REGEX.fullmatch(url))

def validate_email(email: str) -> bool:
    """Validate that *email* conforms to a basic email address format.

    The validation uses a regular expression that checks the local part,
    the ``@`` symbol, and a domain with a top‑level domain.

    Parameters
    ----------
    email: str
        The email address to validate.

    Returns
    -------
    bool
        ``True`` if *email* matches the pattern, otherwise ``False``.
    """
    return bool(EMAIL_REGEX.fullmatch(email))
