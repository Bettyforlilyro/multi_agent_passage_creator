from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.constants import UserConstant
from app.common.exceptions import throw_if, ErrorCode
from app.models import User
from app.schemas import (
    UserRegisterRequest, UserLoginRequest, LoginUserVO,
    UserVO, UserQueryRequest, UserAddRequest,
    DeleteRequest, UserUpdateRequest
)
from app.utils import encrypt_password


class UserService:
    """用户服务"""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, register_request: UserRegisterRequest) -> int:
        """注册用户"""
        throw_if(
            register_request.user_password != register_request.check_password,
            ErrorCode.PARAMS_ERROR,
            "两次输入密码不一致"
        )
        # 检查账户是否已存在
        user_count = await self.db.execute(
            select(func.count(User.id)).where(and_(User.user_account == register_request.user_account))   # type: ignore
        )
        throw_if(
            user_count.scalar_one_or_none() > 0,
            ErrorCode.PARAMS_ERROR,
            "用户账号已存在"
        )
        # 注册用户，先加密密码
        encrypted_password = encrypt_password(register_request.user_password)
        # 插入用户
        user = User(
            user_account=register_request.user_account,
            user_password=encrypted_password,
            user_name=f"用户_{register_request.user_account}",
            user_role=UserConstant.USER,
            quota=UserConstant.DEFAULT_QUOTA,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user.id

    async def login(self, login_request: UserLoginRequest) -> LoginUserVO:
        """登录用户"""
        # 检查用户是否存在
        user = await self.db.execute(
            select(User).where(and_(User.user_account == login_request.user_account, User.is_delete == 0))
        )
        user = user.scalar_one_or_none()
        throw_if(
            user is None,
            ErrorCode.USER_NOT_EXIST,
            "用户不存在"
        )
        # 校验密码
        throw_if(
            user.user_password != encrypt_password(login_request.user_password),
            ErrorCode.PASSWORD_ERROR,
            "密码错误"
        )
        # 登录成功返回登录信息
        return LoginUserVO(
            **user.to_dict()
        )

    async def get_user_by_id(self, user_id: int) -> UserVO:
        """根据用户 ID获取用户信息"""
        user = await self.db.execute(
            select(User).where(and_(User.id == user_id, User.is_delete == 0))
        )
        user = user.scalar_one_or_none()
        throw_if(
            user is None,
            ErrorCode.USER_NOT_EXIST,
            "用户不存在"
        )
        return UserVO(
            **user.to_dict()
        )

    async def list_users_by_page(self, query_request: UserQueryRequest) -> tuple[list[UserVO], int]:
        """根据分页查询用户列表"""
        # 构建查询条件
        conditions = [User.is_delete == 0]
        if query_request.id is not None:
            conditions.append(User.id == query_request.id)
        if query_request.user_account:
            conditions.append(User.user_account.contains(query_request.user_account))
        if query_request.user_name:
            conditions.append(User.user_name.contains(query_request.user_name))
        if query_request.user_profile:
            conditions.append(User.user_profile.contains(query_request.user_profile))
        if query_request.user_role:
            conditions.append(User.user_role == query_request.user_role)

        # 查询总数
        count_stmt = select(func.count(User.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one_or_none() or 0

        # 构建排序
        order_column = User.create_time
        if query_request.sort_field == "createTime":
            order_column = User.create_time
        elif query_request.sort_field == "updateTime":
            order_column = User.update_time
        elif query_request.sort_field == "id":
            order_column = User.id

        # 构建分页查询
        offset = (query_request.current - 1) * query_request.page_size
        stmt = select(User).where(and_(*conditions))
        if query_request.sort_order == "ascend":
            stmt = stmt.order_by(order_column.asc())
        else:
            stmt = stmt.order_by(order_column.desc())
        stmt = stmt.offset(offset).limit(query_request.page_size)

        result = await self.db.execute(stmt)
        users = result.scalars().all()

        # 转换为 VO 列表
        user_vo_list = [UserVO(**user.to_dict()) for user in users]
        return user_vo_list, total

    async def add_user(self, add_request: UserAddRequest) -> int:
        """添加用户"""
        # 检查账户是否已存在
        user_count = await self.db.execute(
            select(func.count(User.id)).where(and_(User.user_account == add_request.user_account))
        )
        throw_if(
            user_count.scalar_one_or_none() > 0,
            ErrorCode.USER_ALREADY_EXIST,
            "用户账号已存在"
        )
        # 加密密码
        encrypted_password = encrypt_password(add_request.user_password)
        # 创建用户
        user = User(
            user_account=add_request.user_account,
            user_password=encrypted_password,
            user_name=add_request.user_name or f"用户_{add_request.user_account}",
            user_avatar=add_request.user_avatar,
            user_profile=add_request.user_profile,
            user_role=add_request.user_role or UserConstant.USER,
            quota=UserConstant.DEFAULT_QUOTA,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user.id

    async def delete_user(self, delete_request: DeleteRequest) -> None:
        """删除用户（软删除）"""
        # 检查用户是否存在
        user = await self.db.execute(
            select(User).where(and_(User.id == delete_request.id, User.is_delete == 0))
        )
        user = user.scalar_one_or_none()
        throw_if(
            user is None,
            ErrorCode.USER_NOT_EXIST,
            "用户不存在"
        )
        # 软删除
        user.is_delete = 1
        await self.db.commit()

    async def update_user(self, update_request: UserUpdateRequest) -> None:
        """更新用户"""
        # 检查用户是否存在
        user = await self.db.execute(
            select(User).where(and_(User.id == update_request.id, User.is_delete == 0))
        )
        user = user.scalar_one_or_none()
        throw_if(
            user is None,
            ErrorCode.USER_NOT_EXIST,
            "用户不存在"
        )
        # 更新字段（仅更新非 None 字段）
        if update_request.user_name is not None:
            user.user_name = update_request.user_name
        if update_request.user_avatar is not None:
            user.user_avatar = update_request.user_avatar
        if update_request.user_profile is not None:
            user.user_profile = update_request.user_profile
        if update_request.user_role is not None:
            user.user_role = update_request.user_role
        await self.db.commit()
