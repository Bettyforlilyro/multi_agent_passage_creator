from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.constants import UserConstant
from app.common.exceptions import throw_if, ErrorCode
from app.models import User
from app.schemas import UserRegisterRequest, UserLoginRequest, LoginUserVO
from app.utils import encrypt_password


class UserService:
    """用户服务"""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, register_request: UserRegisterRequest) -> int:
        """注册用户"""
        # 参数校验
        throw_if(
            len(register_request.user_account) < 4,
            ErrorCode.PARAMS_ERROR,
            "用户账号长度不能小于 4 位"
        )
        throw_if(
            len(register_request.user_password) < 6,
            ErrorCode.PARAMS_ERROR,
            "用户密码长度不能小于 6 位"
        )
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
        # 参数校验
        throw_if(
            len(login_request.user_account) < 4,
            ErrorCode.PARAMS_ERROR,
            "用户账号长度不能小于 4 位"
        )
        throw_if(
            len(login_request.user_password) < 6,
            ErrorCode.PARAMS_ERROR,
            "用户密码长度不能小于 6 位"
        )
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
