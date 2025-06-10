import os
import json

SETTINGS_FILE = "settings.json"

def load_settings() -> dict:
    """
    Загружает настройки из файла settings.json.

    :return: Словарь с настройками.
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Ошибка: Некорректный JSON в settings.json. Используется конфигурация по умолчанию.")
            return {"services": {}}
    return {"services": {}}  # Возвращает дефолтные настройки, если файла нет

def save_settings(settings: dict) -> None:
    """
    Сохраняет настройки в файл settings.json.

    :param settings: Словарь с настройками.
    """
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении настроек: {e}")