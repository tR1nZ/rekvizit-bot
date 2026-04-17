from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from config import TOP_K_RESULTS
from states import SearchState
from utils.formatters import build_prop_browser_text
from utils.keyboards import browser_keyboard

router = Router()

BROWSER_SESSIONS = {}


async def _replace_browser_message(
    *,
    target_message,
    text: str,
    reply_markup,
    photo_file_id: str | None
):
    sent = None

    try:
        if photo_file_id:
            try:
                await target_message.edit_media(
                    media=InputMediaPhoto(media=photo_file_id, caption=text, parse_mode="HTML"),
                    reply_markup=reply_markup
                )
                sent = target_message
            except Exception:
                try:
                    await target_message.delete()
                except Exception:
                    pass
                sent = await target_message.answer_photo(
                    photo=photo_file_id,
                    caption=text,
                    reply_markup=reply_markup
                )
        else:
            try:
                await target_message.edit_text(text, reply_markup=reply_markup)
                sent = target_message
            except Exception:
                try:
                    await target_message.delete()
                except Exception:
                    pass
                sent = await target_message.answer(
                    text,
                    reply_markup=reply_markup
                )
    except Exception:
        pass

    return sent


async def render_browser_message(
    *,
    db,
    target_message,
    user_id: int,
    edit: bool = False
):
    session = BROWSER_SESSIONS.get(user_id)
    if not session:
        if edit:
            try:
                await target_message.edit_text("Сессия просмотра не найдена.")
            except Exception:
                pass
        else:
            await target_message.answer("Сессия просмотра не найдена.")
        return

    items = session["items"]
    page = session["page"]
    total_pages = session["total_pages"]
    mode = session["mode"]
    query = session.get("query")

    if not items:
        if edit:
            try:
                await target_message.edit_text("Ничего не найдено.")
            except Exception:
                pass
        else:
            await target_message.answer("Ничего не найдено.")
        return

    item = items[page]
    prop_id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type = item

    status = await db.get_prop_status(prop_id)
    can_return = await db.user_has_active_issue_for_prop(prop_id, user_id)

    text = build_prop_browser_text(
        page=page,
        total_pages=total_pages,
        prop_id=prop_id,
        name=name,
        description=description,
        gender_group=gender_group,
        item_type=item_type,
        status=status,
        query=query,
        mode=mode
    )

    keyboard = browser_keyboard(
        prop_id=prop_id,
        available_quantity=status["available_quantity"],
        can_return=can_return,
        page=page,
        total_pages=total_pages
    )

    if edit:
        sent = await _replace_browser_message(
            target_message=target_message,
            text=text,
            reply_markup=keyboard,
            photo_file_id=photo_file_id
        )
    else:
        if photo_file_id:
            sent = await target_message.answer_photo(
                photo=photo_file_id,
                caption=text,
                reply_markup=keyboard
            )
        else:
            sent = await target_message.answer(
                text,
                reply_markup=keyboard
            )

    if sent:
        session["chat_id"] = sent.chat.id
        session["message_id"] = sent.message_id
        session["has_photo"] = bool(photo_file_id)


async def refresh_browser_message_for_user(bot, db, user_id: int):
    session = BROWSER_SESSIONS.get(user_id)
    if not session:
        return

    chat_id = session.get("chat_id")
    message_id = session.get("message_id")
    if not chat_id or not message_id:
        return

    class DummyMessage:
        def __init__(self, bot, chat_id, message_id):
            self.bot = bot
            self.chat = type("Chat", (), {"id": chat_id})()
            self.message_id = message_id

        async def edit_media(self, media, reply_markup=None):
            return await self.bot.edit_message_media(
                chat_id=self.chat.id,
                message_id=self.message_id,
                media=media,
                reply_markup=reply_markup
            )

        async def edit_text(self, text, reply_markup=None):
            return await self.bot.edit_message_text(
                chat_id=self.chat.id,
                message_id=self.message_id,
                text=text,
                reply_markup=reply_markup
            )

        async def delete(self):
            return await self.bot.delete_message(
                chat_id=self.chat.id,
                message_id=self.message_id
            )

        async def answer(self, text, reply_markup=None):
            return await self.bot.send_message(
                chat_id=self.chat.id,
                text=text,
                reply_markup=reply_markup
            )

        async def answer_photo(self, photo, caption, reply_markup=None):
            return await self.bot.send_photo(
                chat_id=self.chat.id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup
            )

    msg = DummyMessage(bot, chat_id, message_id)

    await render_browser_message(
        db=db,
        target_message=msg,
        user_id=user_id,
        edit=True
    )


def register_search_handlers(search_service, db):
    @router.message(SearchState.waiting_for_query)
    async def process_search_query(message: Message, state):
        query = (message.text or "").strip()

        if not query:
            await message.answer("Введите запрос для поиска.")
            return

        results = await search_service.hybrid_search(query, top_k=TOP_K_RESULTS)

        if not results:
            await message.answer("Ничего не найдено.")
            await state.clear()
            return

        BROWSER_SESSIONS[message.from_user.id] = {
            "mode": "search",
            "query": query,
            "items": results,
            "page": 0,
            "total_pages": len(results),
        }

        await render_browser_message(
            db=db,
            target_message=message,
            user_id=message.from_user.id,
            edit=False
        )

        await state.clear()

    @router.callback_query(F.data == "browse:prev")
    async def browse_prev(callback: CallbackQuery):
        session = BROWSER_SESSIONS.get(callback.from_user.id)
        if not session:
            await callback.answer("Сессия поиска не найдена.", show_alert=True)
            return

        if session["page"] > 0:
            session["page"] -= 1

        await render_browser_message(
            db=db,
            target_message=callback.message,
            user_id=callback.from_user.id,
            edit=True
        )
        await callback.answer()

    @router.callback_query(F.data == "browse:next")
    async def browse_next(callback: CallbackQuery):
        session = BROWSER_SESSIONS.get(callback.from_user.id)
        if not session:
            await callback.answer("Сессия поиска не найдена.", show_alert=True)
            return

        if session["page"] < session["total_pages"] - 1:
            session["page"] += 1

        await render_browser_message(
            db=db,
            target_message=callback.message,
            user_id=callback.from_user.id,
            edit=True
        )
        await callback.answer()

    @router.callback_query(F.data == "browse:noop")
    async def browse_noop(callback: CallbackQuery):
        await callback.answer()

    return router