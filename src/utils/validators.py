"""Utility validators."""

def validate_ip(ip: str) -> bool:
    """
    Validate an IPv4 address.

    The address must consist of exactly four numeric octets separated by periods.
    Each octet must be in the range 0‑255. Leading zeros are not allowed
    (e.g. ``01`` is considered invalid), and any surrounding whitespace is ignored.
    The function returns ``True`` for a valid address and ``False`` otherwise.

    Edge cases handled:
    * Non‑numeric characters in any octet.
    * Fewer or more than four octets.
    * Octets outside the 0‑255 range.
    * Octets with leading zeros (except the single digit ``0``).
    * Extra whitespace before or after the address.
    """
    # Strip surrounding whitespace
    ip = ip.strip()
    parts = ip.split(".")
    if len(parts) != 4:
        return False

    for part in parts:
        # Empty part or non‑numeric
        if not part.isdigit():
            return False
        # Leading zeros are not allowed unless the octet is exactly "0"
        if len(part) > 1 and part.startswith("0"):
            return False
        value = int(part)
        if value < 0 or value > 255:
            return False

    return True
