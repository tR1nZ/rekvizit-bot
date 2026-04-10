from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from utils.access import is_host

router = Router()


def register_admin_handlers(db):
    @router.message(Command("admins"))
    async def cmd_admins(message: Message):
        user_id = message.from_user.id

        if not is_host(user_id):
            await message.answer("Эта команда доступна только хосту.")
            return

        admins = await db.list_admins()
        if not admins:
            await message.answer("Список админов пуст.")
            return

        lines = ["<b>Список админов:</b>"]
        for admin_user_id, username, full_name in admins:
            display = full_name or "Без имени"
            if username:
                display += f" (@{username})"
            lines.append(f"• {display} — <code>{admin_user_id}</code>")

        await message.answer("\n".join(lines))

    @router.message(Command("add_admin"))
    async def cmd_add_admin(message: Message, command: CommandObject):
        user_id = message.from_user.id

        if not is_host(user_id):
            await message.answer("Эта команда доступна только хосту.")
            return

        arg = (command.args or "").strip()
        if not arg.isdigit():
            await message.answer(
                "Использование:\n<code>/add_admin 123456789</code>\n\n"
                "Пользователь должен сначала написать боту хоть одно сообщение."
            )
            return

        new_admin_id = int(arg)
        added = await db.add_admin(
            user_id=new_admin_id,
            username=None,
            full_name=None
        )

        if added:
            await message.answer(f"✅ Админ добавлен: <code>{new_admin_id}</code>")
        else:
            await message.answer("Этот пользователь уже админ.")

    @router.message(Command("remove_admin"))
    async def cmd_remove_admin(message: Message, command: CommandObject):
        user_id = message.from_user.id

        if not is_host(user_id):
            await message.answer("Эта команда доступна только хосту.")
            return

        arg = (command.args or "").strip()
        if not arg.isdigit():
            await message.answer("Использование:\n<code>/remove_admin 123456789</code>")
            return

        admin_id = int(arg)
        removed = await db.remove_admin(admin_id)

        if removed:
            await message.answer(f"🗑 Админ удален: <code>{admin_id}</code>")
        else:
            await message.answer("Админ с таким ID не найден.")

    @router.message(Command("myid"))
    async def cmd_myid(message: Message):
        username = f"@{message.from_user.username}" if message.from_user.username else "без username"
        await message.answer(
            f"<b>Твой ID:</b> <code>{message.from_user.id}</code>\n"
            f"<b>Username:</b> {username}"
        )

    return router