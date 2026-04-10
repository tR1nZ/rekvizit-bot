from aiogram import Router
from aiogram.types import Message

from utils.keyboards import main_menu_keyboard
from utils.access import can_add_props
from states import SearchState, AddPropState

router = Router()


def register_menu_handlers(db):
    @router.message(lambda message: message.text == "🔍 Найти вещь")
    async def menu_find(message: Message, state):
        await state.set_state(SearchState.waiting_for_query)
        await message.answer(
            "Введите, что нужно найти:",
            reply_markup=main_menu_keyboard()
        )

    @router.message(lambda message: message.text == "➕ Добавить вещь")
    async def menu_add(message: Message, state):
        user_id = message.from_user.id

        if not await can_add_props(db, user_id):
            await message.answer("Только хост и админы могут добавлять реквизит.")
            return

        await state.set_state(AddPropState.waiting_for_name)
        await message.answer(
            "Введите <b>название</b> предмета:",
            reply_markup=main_menu_keyboard()
        )

    return router