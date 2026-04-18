"""Utility validation functions.

Provides validation helpers for common data types.
"""

def validate_ip(ip: str) -> bool:
    """Return True if *ip* is a valid IPv4 address.

    A valid IPv4 address consists of four decimal numbers, each ranging
    from 0 to 255, separated by dots.
    """
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
