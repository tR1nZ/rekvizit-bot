from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import SearchState
from utils.formatters import build_prop_text_for_search
from utils.keyboards import prop_inline_keyboard

router = Router()


def register_search_handlers(search_service, db):
    @router.message(SearchState.waiting_for_query)
    async def process_search_query(message: Message, state: FSMContext):
        query = (message.text or "").strip()

        if not query:
            await message.answer("Введите запрос для поиска.")
            return

        results = await search_service.hybrid_search(query)

        if not results:
            await message.answer("Ничего не найдено.")
            await state.clear()
            return

        await message.answer(f"Найдено результатов: <b>{len(results)}</b>")

        for item in results:
            prop_id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type = item
            status = await db.get_prop_status(prop_id)

            text = build_prop_text_for_search(
                prop_id=prop_id,
                name=name,
                description=description,
                gender_group=gender_group,
                item_type=item_type,
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

        await state.clear()

    return router