import asyncio
import logging
import socket
import ssl

import aiohttp
import certifi

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import (
    BOT_TOKEN,
    DB_PATH,
    EMBEDDING_MODEL_NAME,
    SIMILARITY_THRESHOLD
)
from database import Database
from services import EmbeddingService, SearchService, reminder_loop
from handlers import (
    start_router,
    fallback_router,
    register_add_handlers,
    register_search_handlers,
    register_list_handlers,
    register_issue_handlers,
    register_menu_handlers,
    register_admin_handlers,
    register_my_items_handlers
)

logging.basicConfig(level=logging.INFO)


class CustomAiohttpSession(AiohttpSession):
    async def create_session(self):
        if self._session is None or self._session.closed:
            ssl_context = ssl.create_default_context(cafile=certifi.where())

            connector = aiohttp.TCPConnector(
                family=socket.AF_INET,
                ssl=ssl_context,
                ttl_dns_cache=300,
                limit=10,
            )

            self._session = aiohttp.ClientSession(
                connector=connector,
                trust_env=True,
                headers={"User-Agent": "aiogram-bot"}
            )

        return self._session


async def main():
    if not BOT_TOKEN:
        raise ValueError("Не найден BOT_TOKEN. Укажи его в .env")

    db = Database(DB_PATH)
    await db.init()

    print("Загрузка модели эмбеддингов...")
    embedding_service = EmbeddingService(EMBEDDING_MODEL_NAME)
    print("Модель загружена")

    search_service = SearchService(db, embedding_service, SIMILARITY_THRESHOLD)

    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(register_menu_handlers(db))
    dp.include_router(register_add_handlers(db, embedding_service))
    dp.include_router(register_search_handlers(search_service, db))
    dp.include_router(register_issue_handlers(db))
    dp.include_router(register_list_handlers(db))
    dp.include_router(register_my_items_handlers(db))
    dp.include_router(register_admin_handlers(db))
    dp.include_router(fallback_router)

    session = CustomAiohttpSession()

    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    reminder_task = None

    try:
        me = await bot.get_me()
        print(f"Бот запущен: @{me.username}")

        reminder_task = asyncio.create_task(
            reminder_loop(bot=bot, db=db, interval_hours=24, overdue_days=5)
        )

        await dp.start_polling(bot)
    finally:
        if reminder_task:
            reminder_task.cancel()
            try:
                await reminder_task
            except asyncio.CancelledError:
                pass

        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())