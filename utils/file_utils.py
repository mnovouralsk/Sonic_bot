import os
from PyPDF2 import PdfReader
from datetime import datetime, timedelta

from config import EXTENSION, LIMIT_ELEVEN_LABS
from utils.settings import load_settings, save_settings

def save_temp_file(file_data: bytes, file_path: str) -> None:
    """
    Сохраняет временный файл в папке temp.

    :param file_data: Данные файла в виде байтов.
    :param file_path: Путь для сохранения файла.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_data)

def delete_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_txt(txt_path: str) -> str:
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_text_from_file(filename: str) -> str:
    file_extension = get_file_extension(filename)

    if is_supported_document(file_extension):
        if file_extension == "pdf":
            return extract_text_from_pdf(filename)
        elif file_extension == "txt":
            return extract_text_from_txt(filename)

def get_file_extension(filename: str) -> str:
    return filename.split(".")[-1].lower()

def is_supported_document(file_extension: str) -> bool:
    """ Проверяет, поддерживается ли формат файла (PDF или TXT). """
    return file_extension in EXTENSION

def cleanup_temp_files(unique_id: str):
    """Удаление временных файлов."""
    file_paths = [
        f"data/temp/{unique_id}.mp3",
        f"data/temp/{unique_id}.wav",
        f"data/temp/{unique_id}.pdf",
        f"data/temp/{unique_id}.txt"
    ]

    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Удален файл: {file_path}")
            else:
                print(f"Файл не найден, пропускаем: {file_path}")
        except Exception as e:
            print(f"Ошибка при удалении файла {file_path}: {e}")

def check_service_limit_ElevenLabs(service_name, text_length):
    """Проверить лимит использования сервиса и обновить настройки."""
    settings = load_settings()
    service = settings["services"].get(service_name, {"used_chars": 0, "last_usage": None})

    used_chars = service["used_chars"]
    last_usage = service["last_usage"]

    # Если лимит исчерпан
    if used_chars + text_length > LIMIT_ELEVEN_LABS:
        if last_usage:
            last_usage_date = datetime.fromisoformat(last_usage)
            current_date = datetime.now()

            # Проверка, прошел ли месяц с последнего использования
            if current_date - last_usage_date < timedelta(days=30):
                # Лимит исчерпан и месяц еще не прошел
                print(f"Лимит для {service_name} исчерпан. Используйте другой сервис.")
                return False  # Возвращаем False, чтобы использовать другой сервис
            else:
                # Обновляем дату и обнуляем лимит
                service["used_chars"] = 0
                service["last_usage"] = current_date.isoformat()  # Обновляем на текущую дату
                print(f"Обновляем лимит и дату последнего использования для {service_name}.")
        else:
            # Если это первое использование
            service["last_usage"] = datetime.now().isoformat()
            print(f"Первое использование {service_name}.")

    # Обновляем количество использованных символов
    service["used_chars"] = used_chars + text_length
    settings["services"][service_name] = service  # Обновляем данные о сервисе
    save_settings(settings)
    return True  # Возвращаем True, чтобы продолжить использовать сервис