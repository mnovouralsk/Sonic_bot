import os
from fpdf import FPDF
import subprocess
from pydub import AudioSegment

def convert_text_to_format(text: str, file_format: str, unique_id: str) -> str:
    """
    Конвертирует текст в указанный формат (TXT или PDF).

    :param text: Исходный текст.
    :param file_format: Целевой формат ('txt' или 'pdf').
    :param unique_id: Уникальный идентификатор для имени файла.
    :return: Путь к созданному файлу.
    """
    os.makedirs("data/temp", exist_ok=True)
    output_file = f"data/temp/{unique_id}.{file_format}"

    try:
        if file_format == "txt":
            with open(output_file, "w", encoding="utf-8") as file:
                file.write(text)

        elif file_format == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            font_path = "C:/Windows/Fonts/arial.ttf"  # Укажи путь к ttf-шрифту, если используешь другой
            pdf.add_font("ArialUnicode", style="", fname=font_path, uni=True)
            pdf.set_font("ArialUnicode", size=12)

            pdf.multi_cell(0, 10, text)
            pdf.output(output_file, "F")

    except Exception as e:
        print(f"Ошибка при конвертации текста в {file_format}: {e}")
        return None

    return output_file

def convert_wav_to_mp3_ffmpeg(input_wav: str, output_mp3: str) -> None:
    """
    Конвертирует аудиофайл из WAV в MP3 с использованием FFmpeg.

    :param input_wav: Путь к входному WAV-файлу.
    :param output_mp3: Путь к выходному MP3-файлу.
    :raises FileNotFoundError: Если FFmpeg не установлен.
    :raises RuntimeError: Если конвертация не удалась.
    """
    # Проверяем, установлен ли FFmpeg
    if not is_ffmpeg_installed():
        raise FileNotFoundError("FFmpeg не найден. Установите его и попробуйте снова.")

    # Запуск FFmpeg для конвертации
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_wav, "-codec:a", "libmp3lame", "-qscale:a", "2", output_mp3],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка при конвертации WAV в MP3: {e}")

def is_ffmpeg_installed() -> bool:
    """
    Проверяет, установлен ли FFmpeg в системе.

    :return: True, если FFmpeg доступен, иначе False.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def convert_mp3_to_wav(mp3_path: str, wav_path: str) -> None:
    os.makedirs(os.path.dirname(wav_path), exist_ok=True)

    try:
        audio = AudioSegment.from_file(mp3_path, format="mp3")
        audio = audio.set_frame_rate(16000).set_sample_width(2).set_channels(1)
        audio.export(wav_path, format="wav")
    except Exception as e:
        print(f"Ошибка при конвертировании из mp3 в wav: {e}")