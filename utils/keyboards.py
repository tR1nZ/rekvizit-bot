from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔍 Найти вещь"),
        KeyboardButton(text="📦 Список вещей"),
    )
    builder.row(
        KeyboardButton(text="➕ Добавить вещь"),
    )
    return builder.as_markup(resize_keyboard=True)


def prop_inline_keyboard(prop_id: int, available_quantity: int, taken_count: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if available_quantity > 0:
        builder.button(text="✅ Взять 1", callback_data=f"take:{prop_id}")

    if taken_count > 0:
        builder.button(text="↩️ Вернуть 1", callback_data=f"return:{prop_id}")

    return builder.as_markup()