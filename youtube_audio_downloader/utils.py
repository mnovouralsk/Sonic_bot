import re


def safe_filename(name: str) -> str:
    """
    Очищает название файла от недопустимых символов.
    """
    return re.sub(r'[\\/*?:"<>|]', "_", name)
