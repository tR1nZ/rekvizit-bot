from config import HOST_IDS


def is_host(user_id: int) -> bool:
    return user_id in HOST_IDS


async def can_add_props(db, user_id: int) -> bool:
    if is_host(user_id):
        return True
    return await db.is_admin(user_id)