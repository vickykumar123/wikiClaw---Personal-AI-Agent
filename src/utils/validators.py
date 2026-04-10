def validate_port(port):
    """
    Validate that the given port is an integer between 1 and 65535 inclusive.

    Args:
        port: The port number to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    if isinstance(port, int) and 1 <= port <= 65535:
        return True
    return False
