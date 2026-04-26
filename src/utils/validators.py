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
