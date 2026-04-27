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
