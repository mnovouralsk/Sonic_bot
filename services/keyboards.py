from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

mainMenu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Профиль"),
        KeyboardButton(text="ПРЕМИУМ")
    ]],
    resize_keyboard=True,
    one_time_keyboard=False
)