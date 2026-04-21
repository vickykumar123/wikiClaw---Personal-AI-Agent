# src/utils/validators.py
"""Utility validation functions for URLs and email addresses."""

import re

def validate_url(url: str) -> bool:
    """Return True if *url* matches a simple HTTP/HTTPS URL pattern.

    The pattern checks for an optional scheme (http or https), a domain name
    consisting of alphanumeric characters, hyphens and dots, and an optional
    path. It is not exhaustive but suitable for basic validation.
    """
    pattern = r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$'
    return re.match(pattern, url) is not None


def validate_email(email: str) -> bool:
    """Return True if *email* matches a basic email address pattern.

    The pattern checks for a local part with word characters, dots or hyphens,
    an @ symbol, and a domain part with similar rules followed by a top‑level
    domain.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
