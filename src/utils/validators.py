import re

def validate_url(url: str) -> bool:
    """
    Return True if `url` looks like a valid HTTP/HTTPS URL.
    """
    pattern = re.compile(
        r'^(https?://)?'                     # optional scheme
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'    # domain
        r'(:\d+)?'                           # optional port
        r'(/[a-zA-Z0-9._~:/?#\[\]@!$&\'()*+,;=%-]*)?$'  # optional path and query
    )
    return bool(pattern.match(url))

def validate_email(email: str) -> bool:
    """
    Return True if `email` matches a simple email pattern.
    """
    pattern = re.compile(
        r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    )
    return bool(pattern.match(email))
