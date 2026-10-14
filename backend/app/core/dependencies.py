from typing import AsyncGenerator, Optional

from fastapi import Request, Cookie, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.constants import UserConstant
from app.common.exceptions import BusinessException, ErrorCode
from app.schemas import LoginUserVO
from app.utils import get_session


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


async def get_session_id(session_id: Optional[str] = Cookie(None, alias="SESSION")) -> Optional[str]:
    """获取 Cookie 中的 SESSION ID"""
    return session_id


async def get_current_user(
        session_id: Optional[str] = Depends(get_session_id),
        redis_client: Redis = Depends(get_redis),
) -> Optional[LoginUserVO]:
    """获取当前登录用户"""
    if not session_id:
        return None
    session_data = await get_session(session_id, redis_client=redis_client)
    if not session_data or "userName" not in session_data:
        return None
    user_data = session_data
    return LoginUserVO(**user_data)


async def require_login(current_user: Optional[LoginUserVO] = Depends(get_current_user)) -> LoginUserVO:
    """要求用户登录"""
    if not current_user:
        raise BusinessException(ErrorCode.NOT_LOGIN_ERROR)
    return current_user


async def require_admin(current_user: LoginUserVO = Depends(require_login)) -> LoginUserVO:
    """要求用户是管理员"""
    if current_user.user_role != UserConstant.ADMIN:
        raise BusinessException(ErrorCode.NO_AUTH_ERROR)
    return current_user
