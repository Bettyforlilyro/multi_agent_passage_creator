from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_redis
from app.models import User
from app.schemas import UserVO

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/{user_id}", response_model=UserVO)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    # 先查缓存
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return UserVO.model_validate_json(cached)

    # 异步查询数据库，不阻塞事件循环
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        await redis.set(f"user:{user_id}", user.model_dump_json(), ex=60)
    return user
