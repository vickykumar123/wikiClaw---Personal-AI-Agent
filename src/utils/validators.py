def validate_ip(ip: str) -> bool:
    """Return True if `ip` is a valid IPv4 address.

    The address must consist of four decimal octets separated by dots.
    Each octet must be in the range 0-255, contain only digits, and must not
    have leading zeros unless the octet is exactly "0".
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        # Disallow leading zeros (e.g., "01") unless the part is "0"
        if len(part) > 1 and part[0] == '0':
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True
