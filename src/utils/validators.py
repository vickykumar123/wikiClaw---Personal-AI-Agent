def validate_email(email: str) -> bool:
    return '@' in email and '.' in email


def validate_port(port: int) -> bool:
    return isinstance(port, int) and 1 <= port <= 65535
