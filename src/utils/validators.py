"""Utility validation functions."""


def validate_port(port):
    """Validate that `port` is an integer between 1 and 65535 inclusive.

    Parameters
    ----------
    port : Any
        The value to validate as a port number.

    Returns
    -------
    bool
        ``True`` if *port* is a valid integer port number, ``False`` otherwise.
    """
    # bool is a subclass of int, but should not be considered a valid port
    if isinstance(port, bool):
        return False
    if isinstance(port, int) and 1 <= port <= 65535:
        return True
    return False
