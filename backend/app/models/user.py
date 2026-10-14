"""用户 ORM 模型"""

from datetime import datetime

from sqlalchemy import BigInteger, Integer, String, DateTime, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from . import Base


class User(Base):
    """用户表"""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="id")
    user_account: Mapped[str] = mapped_column("userAccount", String(256), nullable=False, unique=True, comment="账号")
    user_password: Mapped[str] = mapped_column("userPassword", String(512), nullable=False, comment="密码")
    user_name: Mapped[str] = mapped_column("userName", String(256), nullable=True, comment="用户昵称")
    user_avatar: Mapped[str] = mapped_column("userAvatar", String(1024), nullable=True, comment="用户头像")
    user_profile: Mapped[str] = mapped_column("userProfile", String(512), nullable=True, comment="用户简介")
    user_role: Mapped[str] = mapped_column("userRole", String(256), nullable=False, default="user", comment="用户角色：user/admin")
    quota: Mapped[int] = mapped_column("quota", Integer, nullable=False, default=5, comment="剩余配额")
    vip_time: Mapped[datetime] = mapped_column("vipTime", DateTime, nullable=True, comment="成为会员时间")
    edit_time: Mapped[datetime] = mapped_column("editTime", DateTime, nullable=False, default=func.now(), comment="编辑时间")
    create_time: Mapped[datetime] = mapped_column("createTime", DateTime, nullable=False, default=func.now(), comment="创建时间")
    update_time: Mapped[datetime] = mapped_column("updateTime", DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_delete: Mapped[int] = mapped_column("isDelete", SmallInteger, nullable=False, default=0, comment="是否删除")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "userAccount": self.user_account,
            "userName": self.user_name,
            "userAvatar": self.user_avatar,
            "userProfile": self.user_profile,
            "userRole": self.user_role,
            "quota": self.quota,
            "vipTime": self.vip_time.isoformat() if self.vip_time else None,
            "createTime": self.create_time.isoformat() if self.create_time else None,
            "updateTime": self.update_time.isoformat() if self.update_time else None,
        }
