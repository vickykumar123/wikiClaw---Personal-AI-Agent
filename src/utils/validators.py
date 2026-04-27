"""Utility validation functions."""


def validate_port(port: int) -> bool:
    """
    Validate that the given port is an integer between 1 and 65535 inclusive.

    Args:
        port (int): The port number to validate.

    Returns:
        bool: True if the port is within the valid range, False otherwise.
    """
    return isinstance(port, int) and 1 <= port <= 65535


def validate_ip(ip: str) -> bool:
    """
    Validate that the given string is a valid IPv4 address.

    Args:
        ip (str): The IP address to validate.

    Returns:
        bool: True if the IP address consists of four octets each between 0 and 255, False otherwise.
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
