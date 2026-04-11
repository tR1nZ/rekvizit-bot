from aiogram import Router
from aiogram.filters import Command
from handlers.search import BROWSER_SESSIONS, render_browser_message

router = Router()


def register_list_handlers(db):
    @router.message(Command("list"))
    async def cmd_list(message):
        items = await db.list_recent_props(limit=200)

        if not items:
            await message.answer("База пока пустая.")
            return

        BROWSER_SESSIONS[message.from_user.id] = {
            "mode": "list",
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

    @router.message(lambda message: message.text == "📦 Список вещей")
    async def menu_list(message):
        items = await db.list_recent_props(limit=200)

        if not items:
            await message.answer("База пока пустая.")
            return

        BROWSER_SESSIONS[message.from_user.id] = {
            "mode": "list",
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