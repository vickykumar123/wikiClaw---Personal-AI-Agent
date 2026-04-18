def format_timestamp(dt):
    """
    Format a datetime object as a string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text, max_length=100):
    """
    Truncate the given text to `max_length` characters.
    If the text is longer, it returns the first `max_length - 3` characters
    followed by an ellipsis ('...').
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'
