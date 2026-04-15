"""Utility validation functions."""

__all__ = ["validate_ip"]

def validate_ip(ip: str) -> bool:
    """Validate an IPv4 address.

    Args:
        ip: The IP address string to validate.

    Returns:
        True if *ip* is a valid IPv4 address, False otherwise.

    An IPv4 address consists of four decimal numbers (0-255) separated by
    periods. Leading zeros are not permitted unless the octet is exactly
    ``0``. Non‑numeric characters cause validation to fail.
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        if len(part) > 1 and part[0] == '0':
            return False
        num = int(part)
        if not 0 <= num <= 255:
            return False
    return True
