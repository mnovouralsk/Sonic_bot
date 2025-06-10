import logging

logger = logging.getLogger("YouTubeAudioDownloader")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

if not logger.hasHandlers():
    logger.addHandler(console_handler)
