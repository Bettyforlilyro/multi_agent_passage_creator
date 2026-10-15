import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db, get_redis, require_login, get_session_id, require_admin
from app.schemas import (
    BaseResponse, LoginUserVO, UserLoginRequest,
    UserRegisterRequest, UserVO, UserQueryRequest,
    UserAddRequest, DeleteRequest, UserUpdateRequest
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


@router.get("/get", response_model=BaseResponse[UserVO])
async def get_user_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    """根据用户 ID获取用户信息"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(id)
    return BaseResponse.success(data=user, message="获取用户成功")


@router.post("/list/page", response_model=BaseResponse[dict])
async def list_users_by_page(
    request: UserQueryRequest,
    db: AsyncSession = Depends(get_db),
    _: LoginUserVO = Depends(require_admin),
):
    """根据分页查询用户列表（管理员）"""
    user_service = UserService(db)
    users, total = await user_service.list_users_by_page(request)
    return BaseResponse.success(data={
        "records": users,
        "total": total,
        "current": request.current,
        "size": request.size,
    })


@router.post("/add", response_model=BaseResponse[int])
async def add_user(
    request: UserAddRequest,
    db: AsyncSession = Depends(get_db),
    _: LoginUserVO = Depends(require_admin),
):
    """添加用户（管理员）"""
    user_service = UserService(db)
    user_id = await user_service.add_user(request)
    return BaseResponse.success(data=user_id, message="添加用户成功")


@router.post("/delete", response_model=BaseResponse[bool])
async def delete_user(
    request: DeleteRequest,
    db: AsyncSession = Depends(get_db),
    _: LoginUserVO = Depends(require_admin),
):
    """删除用户（管理员）"""
    user_service = UserService(db)
    await user_service.delete_user(request)
    return BaseResponse.success(data=True, message="删除用户成功")


@router.post("/update", response_model=BaseResponse[bool])
async def update_user(
    request: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: LoginUserVO = Depends(require_admin),
):
    """更新用户（管理员）"""
    user_service = UserService(db)
    await user_service.update_user(request)
    return BaseResponse.success(data=True, message="更新用户成功")
