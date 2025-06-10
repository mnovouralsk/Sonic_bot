import os
import uuid
import re
import logging
from aiogram import Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile

from config import EXTENSION
from youtube_audio_downloader.youTubeAudioDownloader import YouTubeAudioDownloader
from models.state import Form
from services.speech_to_text import recognize_text, create_text_file
from services.gpt_service import generate_text_with_gpt, generate_text_ideas_with_gpt
from utils.file_utils import cleanup_temp_files
from services.database import DataBase

router = Router()
database = DataBase()
YOUTUBE_URL_PATTERN = re.compile(
    r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+'
)

@router.message(lambda message: message.text and YOUTUBE_URL_PATTERN.match(message.text.strip()))
async def handle_youtube_url(message: types.Message, state: FSMContext):
    url = message.text.strip()
    await message.answer(f"Получена YouTube-ссылка, скачиваем аудио дорожку...")

    user_id = message.from_user.id
    referal = database.get_referrer_id(user_id)
    isReferralActive = referal != 0

    os.makedirs("data/temp", exist_ok=True)

    unique_id = str(uuid.uuid4())
    file_path = f"data/temp/{unique_id}.mp3"
    wav_file = f"data/temp/{unique_id}.wav"

    try:
        downloader = YouTubeAudioDownloader(url)
        await downloader.download_audio_async(file_path)
        # Сохраняем уникальный ID для дальнейшего использования
        await state.update_data(
            unique_id=unique_id,
            file_path=file_path,
            wav_file=wav_file,
            isReferralActive=isReferralActive)
        # Вызываем процесс обработки форматов сразу после загрузки
        await process_format_selection(message, state)
        # await message.answer_document(FSInputFile(file_path), caption="mp3 файл")

    except Exception as e:
        logging.error(f"Ошибка загрузки аудио: {e}")
        await message.answer("Произошла ошибка при загрузке аудио.")
        if os.path.exists(file_path):
            os.remove(file_path)


@router.message(StateFilter(Form.waiting_for_format))
async def process_format_selection(message: Message, state: FSMContext):
    user_data = await state.get_data()
    unique_id = user_data.get('unique_id')
    file_path = user_data.get('file_path')
    wav_file = user_data.get('wav_file')
    isReferralActive = user_data.get('isReferralActive')

    # Начинаем распознавание текста
    await message.answer("Ожидайте, идет распознавание аудио...")

    try:
        text = recognize_text(file_path, wav_file)
        if not text:
            await message.answer("Не удалось распознать текст.")
            return

        await state.update_data(text=text)
        extension_list = EXTENSION #if isReferralActive else [EXTENSION[0]]

        # if isReferralActive:
        text = generate_text_with_gpt(text)

        for ext in extension_list:
            output_file = create_text_file(text, ext, unique_id)
            if output_file:
                await message.answer_document(FSInputFile(output_file), caption="Ваш файл готов 📄")
            else:
                await message.answer(f"Ошибка: не удалось создать файл формата {ext}.")

        await message.answer(f"создается краткая версия текста")

        # if isReferralActive:
        prompt = "Вот часть текста, сделай краткую версию, убери лишние фразы оставь только основную мысль, оформи в виде урока, выбери остновную мысль или мысли которую он несет, если текст не несет полезной информации, то верни False, сделай читабельно и сделай красивое форматирование текста и не используй Markdown это очень важно. Результат напиши на русском языке кроме False и не дописывай больше ничего лишнего, а только результат верни:\n\n"
        text = generate_text_ideas_with_gpt(text, prompt)

        prompt = "Проанализируй следующий распознанный текст из видео на YouTube. На его основе составь подробный и понятный урок по основной теме видео. Убери лишнюю воду, повторения и неинформативные фразы. Сохрани только важную и полезную информацию, чтобы урок был максимально информативным и легко читался. Не используй разметку markdown и ни какую другую разметку, списки делай с помощью обычных цифр или тире, заголовки выделяй прописными буквами. Возвращай только сам ответ, не добавляй никаких пояснений или комментариев от себя. Ответ возвращай на русском языке.\n\n"
        text = generate_text_ideas_with_gpt(text, prompt)

        for ext in extension_list:
            output_file = create_text_file(text, ext, unique_id)
            if output_file:
                await message.answer_document(FSInputFile(output_file), caption="Ваш файл готов 📄")
            else:
                await message.answer(f"Ошибка: не удалось создать файл формата {ext}.")

    except Exception as e:
        logging.error(f"Ошибка обработки текста: {e}")
        await message.answer("Произошла ошибка при обработке аудиофайла.")

    finally:
        cleanup_temp_files(unique_id)

    # audio = message.audio
    # if audio.mime_type != "audio/mpeg" or audio.duration > 1800:
    #     await message.answer("Файл должен быть MP3 и менее 30 минут.")
    #     return

    # unique_id = str(uuid.uuid4())
    # file_path = f"data/temp/{unique_id}.mp3"
    # wav_file = f"data/temp/{unique_id}.wav"

    # os.makedirs("data/temp", exist_ok=True)

    # try:
    #     file = await message.bot.get_file(audio.file_id)
    #     await message.bot.download_file(file.file_path, file_path)

    #     # Сохраняем уникальный ID для дальнейшего использования
    #     await state.update_data(
    #         unique_id=unique_id,
    #         file_path=file_path,
    #         wav_file=wav_file,
    #         isReferralActive=isReferralActive)

    #     # Вызываем процесс обработки форматов сразу после загрузки
    #     await process_format_selection(message, state)

    # except Exception as e:
    #     logging.error(f"Ошибка загрузки аудио: {e}")
    #     await message.answer("Произошла ошибка при загрузке аудио.")
    #     if os.path.exists(file_path):
    #         os.remove(file_path)

# @router.message(StateFilter(Form.waiting_for_format))
# async def process_format_selection(message: Message, state: FSMContext):
#     user_data = await state.get_data()
#     unique_id = user_data.get('unique_id')
#     file_path = user_data.get('file_path')
#     wav_file = user_data.get('wav_file')
#     isReferralActive = user_data.get('isReferralActive')

#     # Начинаем распознавание текста
#     await message.answer("Ожидайте, идет распознавание аудио...")

#     try:
#         text = recognize_text(file_path, wav_file)
#         if not text:
#             await message.answer("Не удалось распознать текст.")
#             return

#         await state.update_data(text=text)
#         extension_list = EXTENSION if isReferralActive else [EXTENSION[0]]

#         if isReferralActive:
#             text = generate_text_with_gpt(text)

#         for ext in extension_list:
#             output_file = create_text_file(text, ext, unique_id)
#             if output_file:
#                 await message.answer_document(FSInputFile(output_file), caption="Ваш файл готов 📄")
#             else:
#                 await message.answer(f"Ошибка: не удалось создать файл формата {ext}.")

#     except Exception as e:
#         logging.error(f"Ошибка обработки текста: {e}")
#         await message.answer("Произошла ошибка при обработке аудиофайла.")

#     finally:
#         cleanup_temp_files(unique_id)
