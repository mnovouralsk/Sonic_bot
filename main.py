from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging

from config import API_TOKEN
from handlers import url_processing, start, audio_processing, text_processing, photo_processing

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

bot = Bot(token=API_TOKEN)

async def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    router = Router()
    dp.include_router(router)

    dp.include_router(start.router)
    dp.include_router(url_processing.router)
    dp.include_router(audio_processing.router)
    dp.include_router(text_processing.router)
    # dp.include_router(link_processsing.router)
    dp.include_router(photo_processing.router)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: ошибка в функции {main.__name__}: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())  # Запускаем main()
    except KeyboardInterrupt:
        print("Бот выключен")
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}", exc_info=True)