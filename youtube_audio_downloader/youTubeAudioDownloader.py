import os
import subprocess
from typing import Optional
import asyncio

from .exceptions import DownloadError
from .logger import logger
from .utils import safe_filename


class YouTubeAudioDownloader:
    def __init__(self, youtube_url: str):
        """
        Инициализация с URL YouTube.
        """
        self.youtube_url = youtube_url
        logger.info(f"Создан объект загрузчика для URL: {youtube_url}")

    def download_audio(self, output_filename: Optional[str] = None) -> str:
        """
        Скачивает аудио и конвертирует в MP3 через yt-dlp.

        :param output_folder: Каталог для сохранения.
        :param output_filename: Имя файла (если None — используется название видео).
        :return: Путь к сохраненному MP3-файлу.
        """
        try:
            # yt-dlp сам подставит название видео, если имя не указано
            # if output_filename:
            if not output_filename.endswith(".mp3"):
                output_filename += ".mp3"
                # output_template = os.path.join(output_folder, output_filename)
            # else:
                # output_template = os.path.join(output_folder, "%(title)s.%(ext)s")

            cmd = [
                "yt-dlp",
                "-f", "bestaudio",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "-o", output_filename,
                self.youtube_url
            ]

            logger.info(f"Выполняется загрузка через yt-dlp: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)

            logger.info(f"✅ Аудио успешно загружено в {output_filename}")
            return output_filename

        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка выполнения yt-dlp: {e}")
            raise DownloadError("Ошибка при загрузке и конвертации аудио через yt-dlp.")

    async def download_audio_async(self, output_filename: str = "audio.mp3") -> str:
        return await asyncio.to_thread(self.download_audio, output_filename)