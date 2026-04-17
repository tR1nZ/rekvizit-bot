def _format_username(issue: dict) -> str:
    username = issue.get("taken_by_username")
    user_id = issue.get("taken_by_user_id")

    if username:
        return f"@{username}"
    if user_id:
        return f"Пользователь <code>{user_id}</code>"
    return "Неизвестно"


def _format_holder(issue: dict) -> str:
    team_name = issue.get("team_name") or "Без команды"
    user_text = _format_username(issue)
    return f"• {team_name} — {user_text}"


def build_prop_browser_text(
    page: int,
    total_pages: int,
    prop_id: int,
    name: str,
    description: str,
    gender_group: str,
    item_type: str,
    status: dict,
    query: str | None = None,
    mode: str = "search"
) -> str:
    header = f"<b>{page + 1}/{total_pages}</b>"
    if mode == "search" and query:
        header += f" • Поиск: <b>{query}</b>"
    elif mode == "list":
        header += " • Список вещей"
    elif mode == "my_items":
        header += " • Мои взятые вещи"

    active_issues = status.get("active_issues", [])
    if active_issues:
        holders_text = "\n".join(_format_holder(issue) for issue in active_issues[:4])
        if len(active_issues) > 4:
            holders_text += f"\n• И еще: {len(active_issues) - 4}"
        status_text = "Есть на руках"
    else:
        holders_text = "Никто не взял"
        status_text = "Свободно"

    return (
        f"{header}\n\n"
        f"<b>ID:</b> {prop_id}\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Группа:</b> {gender_group}\n"
        f"<b>Тип:</b> {item_type}\n"
        f"<b>Статус:</b> {status_text}\n"
        f"<b>Всего:</b> {status['total_quantity']}\n"
        f"<b>Свободно:</b> {status['available_quantity']}\n"
        f"<b>На руках:</b> {status['taken_count']}\n\n"
        f"<b>Кто взял:</b>\n{holders_text}"
    )


def build_prop_text_with_box(
    prop_id: int,
    name: str,
    description: str,
    box_number: str,
    team_name: str,
    gender_group: str,
    item_type: str,
    total_quantity: int,
    available_quantity: int,
    taken_count: int,
    taken_by_username: str | None,
    taken_by_user_id: int | None
) -> str:
    if taken_by_username:
        taken_by_text = f"@{taken_by_username}"
    elif taken_by_user_id:
        taken_by_text = f"Пользователь <code>{taken_by_user_id}</code>"
    else:
        taken_by_text = "Неизвестно"

    return (
        f"✅ <b>Предмет выдан</b>\n\n"
        f"<b>ID:</b> {prop_id}\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Группа:</b> {gender_group}\n"
        f"<b>Тип:</b> {item_type}\n"
        f"<b>Коробка:</b> {box_number}\n"
        f"<b>Взяла команда:</b> {team_name}\n"
        f"<b>Взял:</b> {taken_by_text}\n"
        f"<b>Всего:</b> {total_quantity}\n"
        f"<b>Свободно:</b> {available_quantity}\n"
        f"<b>На руках:</b> {taken_count}"
    )


def build_return_text(
    prop_id: int,
    name: str,
    description: str,
    gender_group: str,
    item_type: str,
    total_quantity: int,
    available_quantity: int,
    taken_count: int,
    username: str | None,
    user_id: int | None
) -> str:
    if username:
        user_text = f"@{username}"
    elif user_id:
        user_text = f"Пользователь <code>{user_id}</code>"
    else:
        user_text = "Неизвестно"

    return (
        f"↩️ <b>Одна единица возвращена</b>\n\n"
        f"<b>ID:</b> {prop_id}\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Группа:</b> {gender_group}\n"
        f"<b>Тип:</b> {item_type}\n"
        f"<b>Вернул:</b> {user_text}\n"
        f"<b>Всего:</b> {total_quantity}\n"
        f"<b>Свободно:</b> {available_quantity}\n"
        f"<b>На руках:</b> {taken_count}"
    )