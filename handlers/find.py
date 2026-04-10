from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from utils.formatters import build_prop_text

router = Router()


def register_find_handlers(search_service, similarity_threshold: float):
    @router.message(Command("find"))
    async def cmd_find(message: Message, command: CommandObject):
        query = (command.args or "").strip()
        if not query:
            await message.answer("Использование: <code>/find фуражка</code>")
            return

        results = await search_service.hybrid_search(query)

        if not results:
            await message.answer("Ничего не найдено.")
            return

        await message.answer(f"Найдено результатов: <b>{len(results)}</b>")

        for item in results:
            prop_id, name, description, box_number, photo_file_id = item
            text = build_prop_text(prop_id, name, description, box_number)

            if photo_file_id:
                await message.answer_photo(photo=photo_file_id, caption=text)
            else:
                await message.answer(text)

    @router.message(Command("where"))
    async def cmd_where(message: Message, command: CommandObject):
        query = (command.args or "").strip()
        if not query:
            await message.answer("Использование: <code>/where фуражка</code>")
            return

        results = await search_service.hybrid_search(query, top_k=3)

        if not results:
            await message.answer("Ничего не найдено.")
            return

        lines = ["<b>Где это может лежать:</b>"]
        for item in results:
            prop_id, name, description, box_number, photo_file_id = item
            lines.append(f"• ID {prop_id}: <b>{name}</b> — коробка <b>{box_number}</b>")

        await message.answer("\n".join(lines))

    @router.message(Command("similar"))
    async def cmd_similar(message: Message, command: CommandObject):
        query = (command.args or "").strip()
        if not query:
            await message.answer("Использование: <code>/similar фуражка</code>")
            return

        results = await search_service.similar_items(query)

        lines = [f"<b>Похожие предметы по запросу:</b> {query}\n"]
        found_any = False

        for score, item in results:
            prop_id, name, description, box_number, photo_file_id = item

            if score < similarity_threshold:
                continue

            found_any = True
            lines.append(
                f"• ID {prop_id}: <b>{name}</b> — коробка <b>{box_number}</b> "
                f"(похожесть: {score:.2f})"
            )

        if not found_any:
            await message.answer("Похожие предметы не найдены.")
            return

        await message.answer("\n".join(lines))

    return router