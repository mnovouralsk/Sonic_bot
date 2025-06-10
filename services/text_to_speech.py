import pyttsx3
import requests

from config import API_ELEVEN_LABS, URL_ELEVEN_LABS

def text_to_speech_elevenlabs(text: str, unique_id: str) -> str:
    """
    Преобразует текст в аудио с использованием Eleven Labs API.

    :param text: Текст для преобразования в речь.
    :param unique_id: Уникальный идентификатор для имени файла.
    :return: Путь к сохраненному аудиофайлу или None в случае ошибки.
    """
    if not API_ELEVEN_LABS:
        print("API ключ не установлен.")
        return None

    headers = {"xi-api-key": API_ELEVEN_LABS, "Content-Type": "application/json"}
    payload = {"text": text, "model_id": "eleven_multilingual_v2"}

    try:
        response = requests.post(URL_ELEVEN_LABS, headers=headers, json=payload)
        response.raise_for_status()  # Вызывает исключение для статусов 4xx и 5xx

        audio_file = f"data/temp/{unique_id}.mp3"
        with open(audio_file, "wb") as file:
            file.write(response.content)

        print(f"✅ Аудиофайл сохранен: {audio_file}")
        return audio_file

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при сохранении аудиофайла: {e}")
        return None

def text_to_wav_pyttsx3(text: str, output_wav: str) -> None:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    engine.save_to_file(text, output_wav)
    engine.runAndWait()