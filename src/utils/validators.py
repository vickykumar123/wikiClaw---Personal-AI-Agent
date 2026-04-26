"""Utility validation functions for URLs and email addresses.

This module provides simple validation helpers that raise ``ValueError``
when the input does not conform to expected formats. The functions return
``True`` when the validation succeeds, allowing them to be used directly in
assertions or conditional statements.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

__all__: list[str] = ["validate_url", "validate_email", "validate_port"]

def validate_port(port: int) -> bool:
    """Validate a network port number.

    The ``port`` must be an integer in the range 1‑65535 inclusive. If the
    ``port`` is not an integer or falls outside this range, a ``ValueError``
    is raised with an informative message. Returns ``True`` when the port is
    valid.

    Args:
        port: The port number to validate.

    Returns:
        ``True`` if the ``port`` is within the valid range.

    Raises:
        ValueError: If ``port`` is not an integer or is outside the range
            1‑65535.
    """
    if not isinstance(port, int):
        raise ValueError("Port must be an integer.")
    if not (1 <= port <= 65535):
        raise ValueError(f"Port {port} is out of valid range (1-65535).")
    return True


def validate_url(url: str) -> bool:
    """Validate a URL string.

    The function parses the given ``url`` using :func:`urllib.parse.urlparse`
    and ensures that both a scheme (e.g., ``http`` or ``https``) and a network
    location (netloc) are present. If either component is missing, a
    ``ValueError`` is raised.

    Args:
        url: The URL string to validate.

    Returns:
        ``True`` if the URL is syntactically valid.

    Raises:
        ValueError: If ``url`` is empty, missing a scheme, or missing a netloc.
    """
    if not isinstance(url, str) or not url:
        raise ValueError("URL must be a non‑empty string.")

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: '{url}'. Scheme and netloc are required.")

    return True


def validate_email(email: str) -> bool:
    """Validate an email address.

    A regular expression is used to perform a lightweight validation of the
    provided ``email``. The pattern checks for a typical ``local-part@domain``
    structure with common allowed characters. If the email does not match the
    pattern, a ``ValueError`` is raised.

    Args:
        email: The email address to validate.

    Returns:
        ``True`` if the email address matches the validation pattern.

    Raises:
        ValueError: If ``email`` is empty or does not conform to the expected
            email format.
    """
    if not isinstance(email, str) or not email:
        raise ValueError("Email must be a non‑empty string.")

    # Simple email regex covering most common cases.
    email_pattern = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )
    if not email_pattern.fullmatch(email):
        raise ValueError(f"Invalid email address: '{email}'.")

    return True
