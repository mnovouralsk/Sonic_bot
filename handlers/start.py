from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.filters import CommandStart
import logging

from services.database import DataBase
from services import keyboards
from config import BOT_NAME

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

router = Router()
def escape_markdown(text: str) -> str:
            escape_chars = r'_*[]()~`>#+-=|{}.!'
            return ''.join(['\\' + c if c in escape_chars else c for c in text])

@router.message(CommandStart())
async def start_command(message: Message):
    database = DataBase()

    try:
        if not database.user_exists(message.from_user.id):
            # Пользователь не найден, регистрация нового пользователя
            database.add_user(message.from_user.id) # добавили нового пользователя

        if len(message.text) > len("/start"):
            # Извлекаем реферера, если он есть
            referrer = message.text[7:].strip()  # Получаем текст после "/start "

            if referrer and referrer.isdigit():  # Проверяем, что реферер - это число
                referrer_id = int(referrer)
                if referrer_id == message.from_user.id:
                    await message.answer("Вы не можете стать своим собственным рефералом.")
                    return
                else:
                    print("первая проверка реферала")

                # Проверяем, не является ли реферал уже рефералом пользователя
                existing_referrer = database.get_referrer_id(message.from_user.id)
                if existing_referrer is None or existing_referrer == 0:
                    print("вторая проверка реферала, реферала нет")
                else:
                    if existing_referrer == referrer_id:
                        await message.answer("Вы не можете сделать этого пользователя своим рефералом, так как он уже является вашим рефералом.")
                        return

                database.set_referrer_id(referrer_id, message.from_user.id) # добавили нового пользователя
                await message.bot.send_message(referrer_id, "По вашей ссылке зарегистрировался пользователь.")

        welcome_text = escape_markdown(
            "👋 **Приветствую вас!**\n\n"
            "Я — ваш умный помощник, который поможет вам:\n"
            "1. **Распознавать текст** из ссылки на видео YouTube в текстовые форматы: PDF или TXT. 🎤📄\n"
            "2. **Распознавать текст** из аудио в текстовые форматы: PDF или TXT. 🎤📄\n"
            "3. **ChatGPT** корректировка и форматирование распознанного текста.\n"
            "4. **Озвучивать текст** с помощью различных сервисов, включая ElevenLabs или pyttsx3. 🔊✨\n"
            "5. **Развиваться вместе с вами!** В будущем планируем подключить больше сервисов и форматов файлов.\n"
            "6. **Скоро** вы сможете получать текст по ссылке на плэйлист с **YouTube**! 🎥"
            "||**Приведи друга** и получи расширеный функционал!||\n"
        )
        await message.answer(welcome_text, parse_mode="MarkdownV2", reply_markup=keyboards.mainMenu)
        await message.answer("Отправьте файл mp3 для распознования текста, или текстовый файл (txt, pdf) для озвучивания")

    finally:
        database.close_connection()

@router.message(F.text == "Профиль")
async def profile_command(message: Message):
    database = DataBase()
    user_id = message.from_user.id
    referal = database.get_referrer_id(user_id)

    if referal == 0:
        msg_text = escape_markdown(f"У вас нет реферала, сейчас функционал минимальный! Пригласите друга по данной ссылке:\n**Ваш ID**: {user_id}\n**Ваша реферальная ссылка**: `https://t.me/{BOT_NAME}?start={user_id}`")
        await message.answer(msg_text, parse_mode="MarkdownV2")
    else:
        msg_text = escape_markdown(f"Вам доступен расширенный функционал!\n**Ваш ID**: {user_id}\n**Ваш реферал**: {referal}")
        await message.answer(msg_text, parse_mode="MarkdownV2")
    database.close_connection()


@router.message(F.text == "ПРЕМИУМ")
async def premium_command(message: Message):
    await message.answer("В разработке.")


@router.message(F.text == "secret key")
async def secret_key_command(message: Message):
    await message.answer("Вы ввели секретный ключ.")

# @router.message(lambda message: not (message.audio or message.voice or message.document))

@router.my_chat_member()
async def my_chat_member_handler(update: types.ChatMemberUpdated):
    """Обрабатывает изменения в статусе бота у пользователя."""
    if update.chat.type == "private":
        referrer_id = int(update.from_user.id)
        database = DataBase()

        try:
            if update.new_chat_member.status == "kicked":
                # Пользователь заблокировал бота -> сбрасываем его реферала
                user_id = database.get_user_by_referrer(referrer_id)
                if user_id:
                    database.set_referrer_id(int(user_id), 0)
                    await update.from_user.bot.send_message(user_id, "*Ваш реферал заблокировал бота*,\nПригласите другого пользователя по ссылке в меню 'Профиль'", parse_mode="MarkdownV2")
                print(f"Пользователь {referrer_id} заблокировал бота. Реферал сброшен.")

            elif update.new_chat_member.status == "member":
                # Пользователь разблокировал бота -> можно добавить логику (например, логирование)
                print(f"Пользователь {referrer_id} разблокировал бота.")

        finally:
            database.close_connection()