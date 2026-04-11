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


def browser_keyboard(
    prop_id: int,
    available_quantity: int,
    can_return: bool,
    page: int,
    total_pages: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    top_row = []
    if available_quantity > 0:
        top_row.append(("✅ Взять 1", f"take:{prop_id}"))

    if can_return:
        top_row.append(("↩️ Вернуть 1", f"return:{prop_id}"))

    top_row.append((f"{page + 1}/{total_pages}", "browse:noop"))

    for text, data in top_row:
        builder.button(text=text, callback_data=data)

    bottom_row = []
    if page > 0:
        bottom_row.append(("⬅️", "browse:prev"))
    if page < total_pages - 1:
        bottom_row.append(("➡️", "browse:next"))

    for text, data in bottom_row:
        builder.button(text=text, callback_data=data)

    if bottom_row:
        builder.adjust(len(top_row), len(bottom_row))
    else:
        builder.adjust(len(top_row))

    return builder.as_markup()