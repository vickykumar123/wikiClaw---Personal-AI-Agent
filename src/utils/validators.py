def validate_port(port: int) -> bool:
    """Return True if port is between 1 and 65535 inclusive, otherwise False."""
    return 1 <= port <= 65535
