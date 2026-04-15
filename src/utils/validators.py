import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Validate a URL string.

    Returns True if the URL has a valid scheme and network location,
    and matches a simple URL regex pattern.
    """
    if not isinstance(url, str):
        return False

    # Basic URL regex pattern (allows http, https, ftp)
    url_regex = re.compile(
        r'^(?:http|https|ftp)://'                     # scheme
        r'(?:\S+(?::\S*)?@)?'                         # optional user:pass@
        r'(?:[A-Za-z0-9.-]+|\[[^\]]+\])'              # host or IPv6
        r'(?::\d{1,5})?'                              # optional port
        r'(?:[/?#][^\s]*)?$', re.IGNORECASE)

    if not url_regex.match(url):
        return False

    # Further validation using urllib.parse
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

def validate_email(email: str) -> bool:
    """
    Validate an email address using a basic regular expression.
    """
    if not isinstance(email, str):
        return False

    email_regex = re.compile(
        r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    )
    return bool(email_regex.match(email))
