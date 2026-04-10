def build_prop_text_for_search(
    prop_id: int,
    name: str,
    description: str,
    gender_group: str,
    item_type: str,
    status: dict
) -> str:
    status_text = "Свободно"
    if status["taken_count"] > 0 and status["team_name"]:
        status_text = f"На руках у команды: {status['team_name']}"

    return (
        f"<b>ID:</b> {prop_id}\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Группа:</b> {gender_group}\n"
        f"<b>Тип:</b> {item_type}\n"
        f"<b>Статус:</b> {status_text}\n"
        f"<b>Всего:</b> {status['total_quantity']}\n"
        f"<b>Свободно:</b> {status['available_quantity']}\n"
        f"<b>На руках:</b> {status['taken_count']}"
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
    taken_count: int
) -> str:
    return (
        f"✅ <b>Предмет выдан</b>\n\n"
        f"<b>ID:</b> {prop_id}\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Группа:</b> {gender_group}\n"
        f"<b>Тип:</b> {item_type}\n"
        f"<b>Коробка:</b> {box_number}\n"
        f"<b>Взяла команда:</b> {team_name}\n"
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
    taken_count: int
) -> str:
    return (
        f"↩️ <b>Одна единица возвращена</b>\n\n"
        f"<b>ID:</b> {prop_id}\n"
        f"<b>Название:</b> {name}\n"
        f"<b>Описание:</b> {description}\n"
        f"<b>Группа:</b> {gender_group}\n"
        f"<b>Тип:</b> {item_type}\n"
        f"<b>Всего:</b> {total_quantity}\n"
        f"<b>Свободно:</b> {available_quantity}\n"
        f"<b>На руках:</b> {taken_count}"
    )