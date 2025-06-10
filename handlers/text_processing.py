import uuid
from aiogram import Router, types
from aiogram.types import Message
from services.text_to_speech import text_to_speech_elevenlabs, text_to_wav_pyttsx3
from services.file_converter import convert_wav_to_mp3_ffmpeg
from utils.file_utils import extract_text_from_file, check_service_limit_ElevenLabs


router = Router()

@router.message(lambda message: message.document)
async def handle_text_file(message: Message):
    print("Получен документ")
    file = message.document
    if file.mime_type not in {"text/plain", "application/pdf"}:
        await message.answer("Пожалуйста, отправьте PDF или TXT файл.")
        return

    text = await extract_text_from_file(file)
    unique_id = str(uuid.uuid4())
    wav_file = f"data/temp/{unique_id}.wav"
    mp3_file = f"data/temp/{unique_id}.mp3"

    if check_service_limit_ElevenLabs("elevenlabs", len(text)):
       audio_file =  text_to_speech_elevenlabs(text, unique_id)
       if not audio_file:
           text_to_wav_pyttsx3(text, wav_file)
    else:
        text_to_wav_pyttsx3(text, wav_file)
    convert_wav_to_mp3_ffmpeg(wav_file, mp3_file)

    await message.answer_document(types.FSInputFile(mp3_file), caption="Ваш MP3 файл готов 🎙")