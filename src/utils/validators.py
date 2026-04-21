"""Utility validation functions."""

def validate_port(port):
    """
    Validate that `port` is an integer between 1 and 65535 inclusive.

    Parameters
    ----------
    port : any
        The port value to validate.

    Returns
    -------
    bool
        True if `port` is a valid port number, False otherwise.
    """
    return isinstance(port, int) and 1 <= port <= 65535
