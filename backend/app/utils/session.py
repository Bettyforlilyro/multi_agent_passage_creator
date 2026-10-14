import json
from typing import Optional

from redis.asyncio import Redis

from app.core.config import settings


def _get_session_key(session_id: str) -> str:
    """获取 Session Key"""
    return f"session:{session_id}"


async def get_session(session_id: str, redis_client: Redis) -> Optional[dict]:
    """获取 Session 数据"""
    if not redis_client:
        return None

    key = _get_session_key(session_id)
    data = await redis_client.get(key)

    if data:
        return json.loads(data)
    return None


async def set_session(
        session_id: str,
        data: dict,
        redis_client: Redis,
        expire: Optional[int] = None
):
    """设置 Session 数据"""
    if not redis_client:
        return

    key = _get_session_key(session_id)
    expire_time = expire or settings.session_max_age

    await redis_client.setex(
        key,
        expire_time,
        json.dumps(data)
    )


async def remove_session(session_id: str, redis_client: Redis):
    """删除 Session"""
    if not redis_client:
        return

    key = _get_session_key(session_id)
    await redis_client.delete(key)
