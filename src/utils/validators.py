def validate_email(email: str) -> bool:
    return '@' in email and '.' in email


def validate_port(port: int) -> bool:
    return isinstance(port, int) and 1 <= port <= 65535


def validate_ip(ip: str) -> bool:
    return len(ip.split('.')) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip.split('.'))