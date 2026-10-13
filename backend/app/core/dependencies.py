from typing import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """每个请求一个独立的 AsyncSession，请求结束自动关闭。"""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
            await session.commit()      # 无异常则提交
        except Exception:
            await session.rollback()    # 有异常则回滚
            raise


async def get_redis(request: Request):
    """直接复用 lifespan 中创建的 Redis 客户端。"""
    return request.app.state.redis
