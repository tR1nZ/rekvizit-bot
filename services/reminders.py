import asyncio


async def reminder_loop(bot, db, interval_hours: int = 24, overdue_days: int = 5):
    while True:
        try:
            overdue_items = await db.get_overdue_items_for_reminders(days=overdue_days)

            for item in overdue_items:
                issue_id = item[0]
                prop_id = item[1]
                team_name = item[2]
                taken_by_user_id = item[3]
                issued_at = item[6]
                prop_name = item[8]
                prop_description = item[9]

                text = (
                    f"⏰ Напоминание о реквизите\n\n"
                    f"У тебя на руках реквизит уже больше {overdue_days} дней.\n\n"
                    f"<b>ID:</b> {prop_id}\n"
                    f"<b>Название:</b> {prop_name}\n"
                    f"<b>Описание:</b> {prop_description}\n"
                    f"<b>Команда:</b> {team_name}\n"
                    f"<b>Дата выдачи:</b> {issued_at}\n\n"
                    f"Если реквизит уже вернули, отметь это в боте."
                )

                try:
                    await bot.send_message(chat_id=taken_by_user_id, text=text)
                    await db.mark_issue_reminded(issue_id)
                except Exception as e:
                    print(f"Не удалось отправить напоминание user_id={taken_by_user_id}: {e}")

        except Exception as e:
            print(f"Ошибка в reminder_loop: {e}")

        await asyncio.sleep(interval_hours * 60 * 60)