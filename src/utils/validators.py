"""Utility validation functions for network parameters.
"""

def validate_port(port: int) -> bool:
    """Return True if port is an integer between 1 and 65535 inclusive, otherwise False."""
    return isinstance(port, int) and 1 <= port <= 65535


def validate_ip(ip: str) -> bool:
    """Return True if ip is a valid IPv4 address (four octets 0-255), otherwise False."""
    if not isinstance(ip, str):
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        num = int(part)
        if not (0 <= num <= 255):
            return False
    return True
