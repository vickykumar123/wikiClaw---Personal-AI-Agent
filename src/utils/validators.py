"""Utility validation functions.

This module provides validation utilities such as IP address validation.
"""

__all__ = ["validate_ip"]

def validate_ip(ip: str) -> bool:
    """Validate an IPv4 address.

    Args:
        ip: The IP address string to validate.

    Returns:
        True if `ip` is a valid IPv4 address, False otherwise.
    """
    if not isinstance(ip, str):
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True
