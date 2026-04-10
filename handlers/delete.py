from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router()


def register_delete_handlers(db):
    @router.message(Command("delete"))
    async def cmd_delete(message: Message, command: CommandObject):
        arg = (command.args or "").strip()

        if not arg.isdigit():
            await message.answer("Использование: <code>/delete 3</code>")
            return

        prop_id = int(arg)
        deleted = await db.delete_prop(prop_id)

        if deleted:
            await message.answer(f"🗑 Предмет с ID <b>{prop_id}</b> удален.")
        else:
            await message.answer("Предмет с таким ID не найден.")

    return router