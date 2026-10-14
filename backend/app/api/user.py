import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db, get_redis, require_login, get_session_id
from app.schemas import (
    BaseResponse,
    LoginUserVO, UserLoginRequest, UserRegisterRequest
)
from app.services.user_service import UserService
from app.utils.session import set_session, remove_session

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.post("/login", response_model=BaseResponse[LoginUserVO])
async def login(
    request: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    """登录"""
    user_service = UserService(db)
    login_user = await user_service.login(request)
    # 生成 SESSION ID，保存登录 SESSION 到 redis
    session_id = str(uuid.uuid4())
    await set_session(session_id, login_user.model_dump(by_alias=True), redis_client=redis)
    # 设置 Cookie，将 SESSION ID 传递给客户端
    response.set_cookie("SESSION", session_id, httponly=True, samesite='lax', max_age=settings.session_max_age)
    return BaseResponse.success(data=login_user, message="登录成功")


@router.post("/register", response_model=BaseResponse[int])
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """注册"""
    user_service = UserService(db)
    user_id = await user_service.register(request)
    return BaseResponse.success(data=user_id, message="注册成功")


@router.post("/logout", response_model=BaseResponse[bool])
async def logout(
    response: Response,
    session_id: Optional[str] = Depends(get_session_id),
    _: LoginUserVO = Depends(require_login),
    redis: Redis = Depends(get_redis),
):
    """退出登录"""
    if session_id:
        await remove_session(session_id, redis_client=redis)
        response.delete_cookie("SESSION")
    return BaseResponse.success(data=True, message="退出登录成功")


@router.get("/get/login", response_model=BaseResponse[LoginUserVO])
async def get_login_user(
    current_user: LoginUserVO = Depends(require_login),
):
    """获取当前登录用户"""
    return BaseResponse.success(data=current_user)
