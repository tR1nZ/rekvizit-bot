from aiogram import Router
from aiogram.filters import Command

from handlers.search import BROWSER_SESSIONS, render_browser_message

router = Router()


def register_my_items_handlers(db):
    @router.message(Command("my_items"))
    async def cmd_my_items(message):
        items = await db.get_active_issues_by_user(message.from_user.id)

        if not items:
            await message.answer("У тебя сейчас нет взятых вещей.")
            return

        BROWSER_SESSIONS[message.from_user.id] = {
            "mode": "my_items",
            "query": None,
            "items": items,
            "page": 0,
            "total_pages": len(items),
        }

        await render_browser_message(
            db=db,
            target_message=message,
            user_id=message.from_user.id,
            edit=False
        )

    @router.message(lambda message: message.text == "📋 Мои взятые вещи")
    async def menu_my_items(message):
        items = await db.get_active_issues_by_user(message.from_user.id)

        if not items:
            await message.answer("У тебя сейчас нет взятых вещей.")
            return

        BROWSER_SESSIONS[message.from_user.id] = {
            "mode": "my_items",
            "query": None,
            "items": items,
            "page": 0,
            "total_pages": len(items),
        }

        await render_browser_message(
            db=db,
            target_message=message,
            user_id=message.from_user.id,
            edit=False
        )

    return router