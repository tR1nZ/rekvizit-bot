from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.formatters import build_prop_text_for_search
from utils.keyboards import prop_inline_keyboard

router = Router()


def register_list_handlers(db):
    @router.message(Command("list"))
    async def cmd_list(message: Message):
        items = await db.list_recent_props(limit=30)

        if not items:
            await message.answer("База пока пустая.")
            return

        await message.answer(f"<b>Список вещей:</b> {len(items)} шт.")

        for prop_id, name, description, box_number, photo_file_id, total_quantity, gender_group in items:
            status = await db.get_prop_status(prop_id)

            text = build_prop_text_for_search(
                prop_id=prop_id,
                name=name,
                description=description,
                gender_group=gender_group,
                status=status
            )

            keyboard = prop_inline_keyboard(
                prop_id=prop_id,
                available_quantity=status["available_quantity"],
                taken_count=status["taken_count"]
            )

            if photo_file_id:
                await message.answer_photo(
                    photo=photo_file_id,
                    caption=text,
                    reply_markup=keyboard
                )
            else:
                await message.answer(
                    text,
                    reply_markup=keyboard
                )

    @router.message(lambda message: message.text == "📦 Список вещей")
    async def menu_list(message: Message):
        items = await db.list_recent_props(limit=30)

        if not items:
            await message.answer("База пока пустая.")
            return

        await message.answer(f"<b>Список вещей:</b> {len(items)} шт.")

        for prop_id, name, description, box_number, photo_file_id, total_quantity, gender_group in items:
            status = await db.get_prop_status(prop_id)

            text = build_prop_text_for_search(
                prop_id=prop_id,
                name=name,
                description=description,
                gender_group=gender_group,
                status=status
            )

            keyboard = prop_inline_keyboard(
                prop_id=prop_id,
                available_quantity=status["available_quantity"],
                taken_count=status["taken_count"]
            )

            if photo_file_id:
                await message.answer_photo(
                    photo=photo_file_id,
                    caption=text,
                    reply_markup=keyboard
                )
            else:
                await message.answer(
                    text,
                    reply_markup=keyboard
                )

    return router