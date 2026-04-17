import aiosqlite
import numpy as np

from utils.vector import vector_to_blob


class Database:
    def __init__(self, path: str):
        self.path = path

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS props (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    box_number TEXT NOT NULL,
                    photo_file_id TEXT,
                    embedding BLOB,
                    total_quantity INTEGER NOT NULL DEFAULT 1,
                    gender_group TEXT NOT NULL DEFAULT 'унисекс',
                    item_type TEXT NOT NULL DEFAULT 'реквизит'
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS issued_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prop_id INTEGER NOT NULL,
                    team_name TEXT NOT NULL,
                    taken_by_user_id INTEGER,
                    taken_by_username TEXT,
                    taken_by_full_name TEXT,
                    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    returned INTEGER NOT NULL DEFAULT 0,
                    last_reminded_at TIMESTAMP,
                    FOREIGN KEY (prop_id) REFERENCES props(id)
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    username TEXT,
                    full_name TEXT
                )
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_props_name ON props(name)
            """)

            await db.commit()

            await self._ensure_column(db, "issued_items", "taken_by_user_id", "INTEGER")
            await self._ensure_column(db, "issued_items", "taken_by_username", "TEXT")
            await self._ensure_column(db, "issued_items", "taken_by_full_name", "TEXT")
            await self._ensure_column(db, "issued_items", "last_reminded_at", "TIMESTAMP")
            await self._ensure_column(db, "props", "total_quantity", "INTEGER NOT NULL DEFAULT 1")
            await self._ensure_column(db, "props", "gender_group", "TEXT NOT NULL DEFAULT 'унисекс'")
            await self._ensure_column(db, "props", "item_type", "TEXT NOT NULL DEFAULT 'реквизит'")

            await db.commit()

    async def _ensure_column(self, db, table_name: str, column_name: str, column_type: str):
        cursor = await db.execute(f"PRAGMA table_info({table_name})")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]

        if column_name not in column_names:
            await db.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            )

    async def add_prop(
        self,
        name: str,
        description: str,
        box_number: str,
        photo_file_id: str | None,
        embedding: np.ndarray | None,
        total_quantity: int,
        gender_group: str,
        item_type: str
    ) -> int:
        emb_blob = None if embedding is None else vector_to_blob(embedding)

        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                INSERT INTO props (
                    name,
                    description,
                    box_number,
                    photo_file_id,
                    embedding,
                    total_quantity,
                    gender_group,
                    item_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                description,
                box_number,
                photo_file_id,
                emb_blob,
                total_quantity,
                gender_group,
                item_type
            ))
            await db.commit()
            return cursor.lastrowid

    async def get_prop_by_id(self, prop_id: int):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type
                FROM props
                WHERE id = ?
            """, (prop_id,))
            return await cursor.fetchone()

    async def keyword_search(self, query: str, limit: int = 50):
        q = f"%{query.lower()}%"
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type
                FROM props
                WHERE lower(name) LIKE ?
                   OR lower(description) LIKE ?
                   OR lower(gender_group) LIKE ?
                   OR lower(item_type) LIKE ?
                ORDER BY id DESC
                LIMIT ?
            """, (q, q, q, q, limit))
            return await cursor.fetchall()

    async def get_all_props_for_similarity(self):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type, embedding
                FROM props
                WHERE embedding IS NOT NULL
            """)
            return await cursor.fetchall()

    async def list_recent_props(self, limit: int = 200):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT id, name, description, box_number, photo_file_id, total_quantity, gender_group, item_type
                FROM props
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            return await cursor.fetchall()

    async def delete_prop(self, prop_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                DELETE FROM props
                WHERE id = ?
            """, (prop_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def get_active_issues_for_prop(self, prop_id: int):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT id, prop_id, team_name, taken_by_user_id, taken_by_username,
                       taken_by_full_name, issued_at, returned, last_reminded_at
                FROM issued_items
                WHERE prop_id = ? AND returned = 0
                ORDER BY id DESC
            """, (prop_id,))
            rows = await cursor.fetchall()

        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "prop_id": row[1],
                "team_name": row[2],
                "taken_by_user_id": row[3],
                "taken_by_username": row[4],
                "taken_by_full_name": row[5],
                "issued_at": row[6],
                "returned": row[7],
                "last_reminded_at": row[8],
            })
        return result

    async def user_has_active_issue_for_prop(self, prop_id: int, user_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT 1
                FROM issued_items
                WHERE prop_id = ? AND returned = 0 AND taken_by_user_id = ?
                LIMIT 1
            """, (prop_id, user_id))
            row = await cursor.fetchone()
            return row is not None

    async def count_active_issues_for_prop(self, prop_id: int) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT COUNT(*)
                FROM issued_items
                WHERE prop_id = ? AND returned = 0
            """, (prop_id,))
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def get_prop_quantity_info(self, prop_id: int):
        prop = await self.get_prop_by_id(prop_id)
        if not prop:
            return None

        total_quantity = int(prop[5])
        taken_count = await self.count_active_issues_for_prop(prop_id)
        available_quantity = max(0, total_quantity - taken_count)

        return {
            "total_quantity": total_quantity,
            "taken_count": taken_count,
            "available_quantity": available_quantity,
        }

    async def issue_item(
        self,
        prop_id: int,
        team_name: str,
        taken_by_user_id: int | None,
        taken_by_username: str | None,
        taken_by_full_name: str | None
    ) -> bool:
        quantity_info = await self.get_prop_quantity_info(prop_id)
        if not quantity_info:
            return False

        if quantity_info["available_quantity"] <= 0:
            return False

        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                INSERT INTO issued_items (
                    prop_id,
                    team_name,
                    taken_by_user_id,
                    taken_by_username,
                    taken_by_full_name,
                    returned
                )
                VALUES (?, ?, ?, ?, ?, 0)
            """, (
                prop_id,
                team_name,
                taken_by_user_id,
                taken_by_username,
                taken_by_full_name
            ))
            await db.commit()
            return True

    async def return_item_by_user(self, prop_id: int, user_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT id
                FROM issued_items
                WHERE prop_id = ? AND returned = 0 AND taken_by_user_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (prop_id, user_id))
            row = await cursor.fetchone()

            if not row:
                return False

            issue_id = row[0]

            cursor = await db.execute("""
                UPDATE issued_items
                SET returned = 1
                WHERE id = ?
            """, (issue_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def get_prop_status(self, prop_id: int):
        quantity_info = await self.get_prop_quantity_info(prop_id)
        active_issues = await self.get_active_issues_for_prop(prop_id)

        if quantity_info is None:
            return {
                "is_taken": False,
                "team_name": None,
                "total_quantity": 0,
                "taken_count": 0,
                "available_quantity": 0,
                "active_issues": [],
            }

        latest_team = active_issues[0]["team_name"] if active_issues else None

        return {
            "is_taken": quantity_info["taken_count"] > 0,
            "team_name": latest_team,
            "total_quantity": quantity_info["total_quantity"],
            "taken_count": quantity_info["taken_count"],
            "available_quantity": quantity_info["available_quantity"],
            "active_issues": active_issues,
        }

    async def is_admin(self, user_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT 1
                FROM admins
                WHERE user_id = ?
                LIMIT 1
            """, (user_id,))
            row = await cursor.fetchone()
            return row is not None

    async def add_admin(self, user_id: int, username: str | None, full_name: str | None) -> bool:
        async with aiosqlite.connect(self.path) as db:
            try:
                await db.execute("""
                    INSERT INTO admins (user_id, username, full_name)
                    VALUES (?, ?, ?)
                """, (user_id, username, full_name))
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def remove_admin(self, user_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                DELETE FROM admins
                WHERE user_id = ?
            """, (user_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def list_admins(self):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT user_id, username, full_name
                FROM admins
                ORDER BY id DESC
            """)
            return await cursor.fetchall()

    async def get_overdue_items_for_reminders(self, days: int = 5):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT
                    ii.id,
                    ii.prop_id,
                    ii.team_name,
                    ii.taken_by_user_id,
                    ii.taken_by_username,
                    ii.taken_by_full_name,
                    ii.issued_at,
                    ii.last_reminded_at,
                    p.name,
                    p.description
                FROM issued_items ii
                JOIN props p ON p.id = ii.prop_id
                WHERE ii.returned = 0
                  AND ii.taken_by_user_id IS NOT NULL
                  AND datetime(ii.issued_at) <= datetime('now', ?)
                  AND (
                        ii.last_reminded_at IS NULL
                        OR date(ii.last_reminded_at) < date('now')
                  )
            """, (f"-{days} days",))
            return await cursor.fetchall()

    async def mark_issue_reminded(self, issue_id: int):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
                UPDATE issued_items
                SET last_reminded_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (issue_id,))
            await db.commit()

    async def get_active_issues_by_user(self, user_id: int):
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("""
                SELECT
                    p.id,
                    p.name,
                    p.description,
                    p.box_number,
                    p.photo_file_id,
                    p.total_quantity,
                    p.gender_group,
                    p.item_type
                FROM issued_items ii
                JOIN props p ON p.id = ii.prop_id
                WHERE ii.returned = 0
                  AND ii.taken_by_user_id = ?
                GROUP BY p.id
                ORDER BY MAX(ii.id) DESC
            """, (user_id,))
            return await cursor.fetchall()