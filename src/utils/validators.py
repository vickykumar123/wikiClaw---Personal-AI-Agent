def validate_port(port):
    """Return True if port is an integer between 1 and 65535 inclusive."""
    return isinstance(port, int) and 1 <= port <= 65535
