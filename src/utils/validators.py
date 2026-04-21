def validate_email(email: str) -> bool:
    return '@' in email and '.' in email


def validate_port(port: int) -> bool:
    """Validate that the port number is between 1 and 65535 inclusive."""
    return 1 <= port <= 65535
