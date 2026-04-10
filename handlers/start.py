from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.keyboards import main_menu_keyboard
from utils.access import is_host

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    extra = ""
    if is_host(message.from_user.id):
        extra = (
            "\n\n<b>Команды хоста:</b>\n"
            "/myid — показать свой ID\n"
            "/admins — список админов\n"
            "/add_admin ID — добавить админа\n"
            "/remove_admin ID — удалить админа"
        )

    await message.answer(
        "Привет! Я бот для учета реквизита.\n\n"
        "Используй кнопки ниже."
        + extra,
        reply_markup=main_menu_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    extra = ""
    if is_host(message.from_user.id):
        extra = (
            "\n\n<b>Команды хоста:</b>\n"
            "/myid — показать свой ID\n"
            "/admins — список админов\n"
            "/add_admin ID — добавить админа\n"
            "/remove_admin ID — удалить админа"
        )

    await message.answer(
        "Что умеет бот:\n\n"
        "🔍 Найти вещь\n"
        "📦 Посмотреть список вещей\n"
        "➕ Добавить вещь — только хост и админы\n\n"
        "Под найденной вещью можно нажать <b>Взять</b>.\n"
        "После ввода названия команды бот покажет коробку.\n"
        "У занятой вещи доступна кнопка <b>Вернуть</b>."
        + extra,
        reply_markup=main_menu_keyboard()
    )