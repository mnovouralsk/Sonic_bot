class YouTubeAudioDownloaderError(Exception):
    """
    Базовое исключение для библиотеки YouTubeAudioDownloader.
    Используется для перехвата всех исключений, специфичных для этой библиотеки.
    """
    pass


class DownloadError(YouTubeAudioDownloaderError):
    """
    Исключение, возникающее при ошибках загрузки аудио с YouTube.
    Например, если аудиопоток не найден, файл не удалось сохранить и т.д.
    """
    def __init__(self, message: str):
        super().__init__(f"Ошибка загрузки: {message}")
