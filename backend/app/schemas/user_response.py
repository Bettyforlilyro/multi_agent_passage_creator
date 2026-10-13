"""用户相关请求/响应模型"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator

from .base import PageRequest


class UserRegisterRequest(BaseModel):
    """用户注册请求"""

    user_account: str = Field(..., min_length=4, max_length=256, alias="user_account", description="账号")
    user_password: str = Field(..., min_length=8, max_length=512, alias="user_password", description="密码")
    check_password: str = Field(..., min_length=8, max_length=512, alias="check_password", description="确认密码")


class UserLoginRequest(BaseModel):
    """用户登录请求"""

    user_account: str = Field(..., min_length=4, max_length=256, alias="user_account", description="账号")
    user_password: str = Field(..., min_length=8, max_length=512, alias="user_password", description="密码")


class UserAddRequest(BaseModel):
    """添加用户请求（管理员）"""

    user_account: str = Field(..., alias="user_account", description="账号")
    user_password: str = Field(..., alias="user_password", description="密码")
    user_name: Optional[str] = Field(None, alias="user_name", description="用户昵称")
    user_avatar: Optional[str] = Field(None, alias="user_avatar", description="用户头像")
    user_profile: Optional[str] = Field(None, alias="user_profile", description="用户简介")
    user_role: str = Field(default="user", alias="user_role", description="用户角色")


class UserUpdateRequest(BaseModel):
    """更新用户请求（管理员）"""

    id: int = Field(..., description="用户 ID")
    user_name: Optional[str] = Field(None, alias="user_name", description="用户昵称")
    user_avatar: Optional[str] = Field(None, alias="user_avatar", description="用户头像")
    user_profile: Optional[str] = Field(None, alias="user_profile", description="用户简介")
    user_role: Optional[str] = Field(None, alias="user_role", description="用户角色")


class UserQueryRequest(PageRequest):
    """用户查询请求"""

    id: Optional[int] = Field(None, description="用户 ID")
    user_account: Optional[str] = Field(None, alias="user_account", description="账号")
    user_name: Optional[str] = Field(None, alias="user_name", description="用户昵称")
    user_profile: Optional[str] = Field(None, alias="user_profile", description="用户简介")
    user_role: Optional[str] = Field(None, alias="user_role", description="用户角色")


class UserVO(BaseModel):
    """用户视图对象"""

    id: int
    user_account: str = Field(..., alias="user_account")
    user_name: Optional[str] = Field(None, alias="user_name")
    user_avatar: Optional[str] = Field(None, alias="user_avatar")
    user_profile: Optional[str] = Field(None, alias="user_profile")
    user_role: str = Field(..., alias="user_role")
    quota: Optional[int] = Field(None, description="剩余配额")
    vip_time: Optional[str] = Field(None, alias="vip_time", description="成为会员时间")
    create_time: str = Field(..., alias="create_time")

    class Config:
        populate_by_name = True


class LoginUserVO(BaseModel):
    """登录用户视图对象"""

    id: int
    user_account: str = Field(..., alias="user_account")
    user_name: Optional[str] = Field(None, alias="user_name")
    user_avatar: Optional[str] = Field(None, alias="user_avatar")
    user_profile: Optional[str] = Field(None, alias="user_profile")
    user_role: str = Field(..., alias="user_role")
    quota: Optional[int] = Field(None, description="剩余配额")
    vip_time: Optional[str] = Field(None, alias="vip_time", description="成为会员时间")
    create_time: str = Field(..., alias="create_time")
    update_time: str = Field(..., alias="update_time")

    class Config:
        populate_by_name = True
