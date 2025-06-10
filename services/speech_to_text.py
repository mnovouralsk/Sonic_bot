import os
import json
import vosk
import wave
from pydub import AudioSegment
from pydub.utils import which

from config import MODEL_PATH
from services.file_converter import convert_mp3_to_wav, convert_text_to_format

AudioSegment.converter = which("ffmpeg")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Модель по пути {MODEL_PATH} не найдена.")
model = vosk.Model(MODEL_PATH)

def recognize_text(mp3_file: str, wav_file: str) -> str:
    try:
        convert_mp3_to_wav(mp3_file, wav_file)
        return audio_transcriber(wav_file)
    except Exception as e:
        print(f"Ошибка при распознавании текста: {e}")
        return None

def audio_transcriber(wav_file: str) -> str:
    try:
        with wave.open(wav_file, "rb") as wf:
            recognizer = vosk.KaldiRecognizer(model, wf.getframerate())
            text = ""
            while True:
                data = wf.readframes(1024 * 8)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    text += json.loads(recognizer.Result()).get("text", "") + " "
            return text.strip()
    except Exception as e:
        print(f"Ошибка при транскрибировании аудио: {e}")
        return None

def create_text_file(text: str, file_format: str, unique_id: str) -> str:
    try:
        return convert_text_to_format(text, file_format, unique_id)
    except Exception as e:
        print(f"Ошибка при создании текстового файла: {e}")
        return None