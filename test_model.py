import asyncio
import aiosqlite

from config import DB_PATH, EMBEDDING_MODEL_NAME
from services.embedding import EmbeddingService
from utils.vector import vector_to_blob


async def ensure_column(db, table_name: str, column_name: str, column_type: str):
    cursor = await db.execute(f"PRAGMA table_info({table_name})")
    columns = await cursor.fetchall()
    column_names = [col[1] for col in columns]

    if column_name not in column_names:
        await db.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        )


async def main():
    async with aiosqlite.connect(DB_PATH) as db:
        await ensure_column(db, "props", "total_quantity", "INTEGER NOT NULL DEFAULT 1")
        await ensure_column(db, "props", "gender_group", "TEXT NOT NULL DEFAULT 'унисекс'")
        await ensure_column(db, "props", "item_type", "TEXT NOT NULL DEFAULT 'реквизит'")
        await db.commit()

    print("Загрузка модели...")
    embedding_service = EmbeddingService(EMBEDDING_MODEL_NAME)
    print("Модель загружена")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT id, name, description, box_number, gender_group, item_type
            FROM props
        """)
        rows = await cursor.fetchall()

        for prop_id, name, description, box_number, gender_group, item_type in rows:
            text = (
                f"{name}. {description}. "
                f"Группа: {gender_group}. "
                f"Тип: {item_type}. "
                f"Коробка: {box_number}"
            )
            emb = embedding_service.encode_text(text)
            emb_blob = vector_to_blob(emb)

            await db.execute("""
                UPDATE props
                SET embedding = ?
                WHERE id = ?
            """, (emb_blob, prop_id))

        await db.commit()

    print("Переиндексация завершена")


if __name__ == "__main__":
    asyncio.run(main())