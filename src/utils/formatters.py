import datetime

def format_timestamp(dt: datetime.datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return '.' * max_length
    return text[:max_length - 3] + '...'
