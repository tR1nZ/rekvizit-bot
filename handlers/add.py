from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states import AddPropState
from utils.access import can_add_props

router = Router()


def register_add_handlers(db, embedding_service):
    @router.message(Command("add"))
    async def cmd_add(message: Message, state: FSMContext):
        user_id = message.from_user.id

        if not await can_add_props(db, user_id):
            await message.answer("Только хост и админы могут добавлять реквизит.")
            return

        await state.set_state(AddPropState.waiting_for_name)
        await message.answer("Введите <b>название</b> предмета:")

    @router.message(AddPropState.waiting_for_name)
    async def add_name(message: Message, state: FSMContext):
        name = (message.text or "").strip()
        if not name:
            await message.answer("Название не должно быть пустым. Введите еще раз:")
            return

        await state.update_data(name=name)
        await state.set_state(AddPropState.waiting_for_description)
        await message.answer("Введите <b>описание</b> предмета:")

    @router.message(AddPropState.waiting_for_description)
    async def add_description(message: Message, state: FSMContext):
        description = (message.text or "").strip()
        if not description:
            await message.answer("Описание не должно быть пустым. Введите еще раз:")
            return

        await state.update_data(description=description)
        await state.set_state(AddPropState.waiting_for_box_number)
        await message.answer("Введите <b>номер коробки</b>:")

    @router.message(AddPropState.waiting_for_box_number)
    async def add_box(message: Message, state: FSMContext):
        box_number = (message.text or "").strip()
        if not box_number:
            await message.answer("Номер коробки не должен быть пустым. Введите еще раз:")
            return

        await state.update_data(box_number=box_number)
        await state.set_state(AddPropState.waiting_for_quantity)
        await message.answer("Введите <b>количество</b> этих вещей:")

    @router.message(AddPropState.waiting_for_quantity)
    async def add_quantity(message: Message, state: FSMContext):
        text = (message.text or "").strip()

        if not text.isdigit():
            await message.answer("Количество должно быть целым положительным числом.")
            return

        quantity = int(text)
        if quantity <= 0:
            await message.answer("Количество должно быть больше нуля.")
            return

        await state.update_data(total_quantity=quantity)
        await state.set_state(AddPropState.waiting_for_gender_group)
        await message.answer(
            "Введите группу вещи:\n"
            "<code>мужское</code>, <code>женское</code> или <code>унисекс</code>"
        )

    @router.message(AddPropState.waiting_for_gender_group)
    async def add_gender_group(message: Message, state: FSMContext):
        gender_group = (message.text or "").strip().lower()

        allowed = {"мужское", "женское", "унисекс"}
        if gender_group not in allowed:
            await message.answer(
                "Нужно ввести одно из значений:\n"
                "<code>мужское</code>, <code>женское</code> или <code>унисекс</code>"
            )
            return

        await state.update_data(gender_group=gender_group)
        await state.set_state(AddPropState.waiting_for_item_type)
        await message.answer(
            "Введите тип:\n"
            "<code>одежда</code> или <code>реквизит</code>"
        )

    @router.message(AddPropState.waiting_for_item_type)
    async def add_item_type(message: Message, state: FSMContext):
        item_type = (message.text or "").strip().lower()

        allowed = {"одежда", "реквизит"}
        if item_type not in allowed:
            await message.answer(
                "Нужно ввести одно из значений:\n"
                "<code>одежда</code> или <code>реквизит</code>"
            )
            return

        await state.update_data(item_type=item_type)
        await state.set_state(AddPropState.waiting_for_photo)
        await message.answer(
            "Отправьте <b>фото</b> предмета.\n"
            "Если фото не нужно, напишите <code>нет</code>"
        )

    @router.message(AddPropState.waiting_for_photo, F.photo)
    async def add_photo(message: Message, state: FSMContext):
        data = await state.get_data()

        name = data["name"]
        description = data["description"]
        box_number = data["box_number"]
        total_quantity = data["total_quantity"]
        gender_group = data["gender_group"]
        item_type = data["item_type"]
        photo_file_id = message.photo[-1].file_id

        text_for_embedding = (
            f"{name}. {description}. "
            f"Группа: {gender_group}. "
            f"Тип: {item_type}. "
            f"Коробка: {box_number}"
        )
        emb = embedding_service.encode_text(text_for_embedding)

        prop_id = await db.add_prop(
            name=name,
            description=description,
            box_number=box_number,
            photo_file_id=photo_file_id,
            embedding=emb,
            total_quantity=total_quantity,
            gender_group=gender_group,
            item_type=item_type
        )

        await state.clear()
        await message.answer(
            f"✅ Предмет добавлен. ID: <b>{prop_id}</b>\n"
            f"<b>Количество:</b> {total_quantity}\n"
            f"<b>Группа:</b> {gender_group}\n"
            f"<b>Тип:</b> {item_type}"
        )

    @router.message(AddPropState.waiting_for_photo)
    async def add_without_photo(message: Message, state: FSMContext):
        text = (message.text or "").strip().lower()

        if text != "нет":
            await message.answer("Отправьте фото или напишите <code>нет</code>.")
            return

        data = await state.get_data()

        name = data["name"]
        description = data["description"]
        box_number = data["box_number"]
        total_quantity = data["total_quantity"]
        gender_group = data["gender_group"]
        item_type = data["item_type"]

        text_for_embedding = (
            f"{name}. {description}. "
            f"Группа: {gender_group}. "
            f"Тип: {item_type}. "
            f"Коробка: {box_number}"
        )
        emb = embedding_service.encode_text(text_for_embedding)

        prop_id = await db.add_prop(
            name=name,
            description=description,
            box_number=box_number,
            photo_file_id=None,
            embedding=emb,
            total_quantity=total_quantity,
            gender_group=gender_group,
            item_type=item_type
        )

        await state.clear()
        await message.answer(
            f"✅ Предмет добавлен без фото. ID: <b>{prop_id}</b>\n"
            f"<b>Количество:</b> {total_quantity}\n"
            f"<b>Группа:</b> {gender_group}\n"
            f"<b>Тип:</b> {item_type}"
        )

    return router