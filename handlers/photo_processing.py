import os
import uuid
import logging
from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import FSInputFile

from models.state import Form
from services.speech_to_text import recognize_text, create_text_file
from services.gpt_service import generate_text_with_gpt
from utils.file_utils import cleanup_temp_files
from services.database import DataBase
from config import EXTENSION

router = Router()

@router.message(F.photo)
async def get_id_photo(message: Message):
    # получаем id файла
    file_id = message.photo[-1].file_id
    await message.answer(f"ID файла: {file_id}")