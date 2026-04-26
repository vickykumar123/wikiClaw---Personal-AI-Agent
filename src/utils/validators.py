def validate_email(email: str) -> bool:
    return '@' in email and '.' in email


def validate_port(port: int) -> bool:
    """
    Validate that a port number is within the valid range of 1 to 65535 inclusive.

    Args:
        port (int): The port number to validate.

    Returns:
        bool: True if the port is within the range, False otherwise.
    """
    return 1 <= port <= 65535


def validate_ip(ip: str) -> bool:
    """
    Validate that the given string is a valid IPv4 address.

    The address must consist of four octets separated by periods, with each octet
    being an integer between 0 and 255 inclusive.

    Args:
        ip (str): The IPv4 address to validate.

    Returns:
        bool: True if `ip` is a valid IPv4 address, False otherwise.
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if not 0 <= num <= 255:
            return False
    return True
