def validate_ip(ip: str) -> bool:
    """
    Validate an IPv4 address.

    The function checks that the input string consists of exactly four
    dot-separated octets. Each octet must be an integer in the range
    0 to 255 inclusive. Leading zeros are allowed (e.g., "001.002.003.004").

    Parameters
    ----------
    ip : str
        The IPv4 address string to validate.

    Returns
    -------
    bool
        True if `ip` is a valid IPv4 address, False otherwise.
    """
    # Split the address into parts
    parts = ip.split('.')
    if len(parts) != 4:
        return False

    for part in parts:
        # Each part must be numeric
        if not part.isdigit():
            return False
        # Convert to integer and check range
        num = int(part)
        if num < 0 or num > 255:
            return False

    return True