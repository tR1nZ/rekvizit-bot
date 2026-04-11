from aiogram import Router, F

from states import IssueState
from utils.formatters import build_prop_text_with_box, build_return_text
from handlers.search import refresh_browser_message_for_user

router = Router()


def register_issue_handlers(db):
    @router.callback_query(F.data.startswith("take:"))
    async def take_item_callback(callback, state):
        prop_id = int(callback.data.split(":")[1])

        quantity_info = await db.get_prop_quantity_info(prop_id)
        if not quantity_info:
            await callback.answer("Предмет не найден.", show_alert=True)
            return

        if quantity_info["available_quantity"] <= 0:
            await callback.answer("Свободных единиц больше нет.", show_alert=True)
            return

        await state.update_data(prop_id=prop_id)
        await state.set_state(IssueState.waiting_for_team_name)

        await callback.message.answer(
            "Введите название команды, которая берет эту вещь:"
        )
        await callback.answer()

    @router.message(IssueState.waiting_for_team_name)
    async def process_team_name(message, state):
        team_name = (message.text or "").strip()

        if not team_name:
            await message.answer("Название команды не должно быть пустым.")
            return

        data = await state.get_data()
        prop_id = data.get("prop_id")

        if not prop_id:
            await state.clear()
            await message.answer("Ошибка состояния. Попробуйте снова.")
            return

        user = message.from_user
        full_name = " ".join(
            part for part in [user.first_name, user.last_name] if part
        ).strip() or None

        success = await db.issue_item(
            prop_id=prop_id,
            team_name=team_name,
            taken_by_user_id=user.id,
            taken_by_username=user.username,
            taken_by_full_name=full_name
        )
        if not success:
            await state.clear()
            await message.answer("Свободных единиц этой вещи больше нет.")
            return

        prop = await db.get_prop_by_id(prop_id)
        if not prop:
            await state.clear()
            await message.answer("Предмет не найден.")
            return

        quantity_info = await db.get_prop_quantity_info(prop_id)
        if not quantity_info:
            await state.clear()
            await message.answer("Ошибка количества. Попробуйте снова.")
            return

        prop_id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type = prop

        text = build_prop_text_with_box(
            prop_id=prop_id,
            name=name,
            description=description,
            box_number=box_number,
            team_name=team_name,
            gender_group=gender_group,
            item_type=item_type,
            total_quantity=quantity_info["total_quantity"],
            available_quantity=quantity_info["available_quantity"],
            taken_count=quantity_info["taken_count"],
            taken_by_username=user.username,
            taken_by_user_id=user.id
        )

        await message.answer(text)
        await refresh_browser_message_for_user(message.bot, db, user.id)
        await state.clear()

    @router.callback_query(F.data.startswith("return:"))
    async def return_item_callback(callback):
        prop_id = int(callback.data.split(":")[1])

        can_return = await db.user_has_active_issue_for_prop(prop_id, callback.from_user.id)
        if not can_return:
            await callback.answer("Ты не можешь вернуть эту вещь: ты ее не брал.", show_alert=True)
            return

        success = await db.return_item_by_user(prop_id, callback.from_user.id)
        if not success:
            await callback.answer("Не удалось вернуть вещь.", show_alert=True)
            return

        prop = await db.get_prop_by_id(prop_id)
        if not prop:
            await callback.answer("Предмет не найден.", show_alert=True)
            return

        quantity_info = await db.get_prop_quantity_info(prop_id)
        if not quantity_info:
            await callback.answer("Ошибка количества.", show_alert=True)
            return

        prop_id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type = prop

        text = build_return_text(
            prop_id=prop_id,
            name=name,
            description=description,
            gender_group=gender_group,
            item_type=item_type,
            total_quantity=quantity_info["total_quantity"],
            available_quantity=quantity_info["available_quantity"],
            taken_count=quantity_info["taken_count"],
            username=callback.from_user.username,
            user_id=callback.from_user.id
        )

        await callback.message.answer(text)
        await refresh_browser_message_for_user(callback.bot, db, callback.from_user.id)
        await callback.answer("Одна единица возвращена")

    return router