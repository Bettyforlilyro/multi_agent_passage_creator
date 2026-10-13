"""用户 ORM 模型"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, SmallInteger
from sqlalchemy.sql import func


class User(DeclarativeBase):
    """用户表"""

    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="id")
    user_account = Column("user_account", String(256), nullable=False, unique=True, comment="账号")
    user_password = Column("user_password", String(512), nullable=False, comment="密码")
    user_name = Column("user_name", String(256), nullable=True, comment="用户昵称")
    user_avatar = Column("user_avatar", String(1024), nullable=True, comment="用户头像")
    user_profile = Column("user_profile", String(512), nullable=True, comment="用户简介")
    user_role = Column("user_role", String(256), nullable=False, default="user", comment="用户角色：user/admin")
    quota = Column("quota", Integer, nullable=False, default=5, comment="剩余配额")
    vip_time = Column("vip_time", DateTime, nullable=True, comment="成为会员时间")

    edit_time = Column("edit_time", DateTime, nullable=False, default=func.now(), comment="编辑时间")
    create_time = Column("create_time", DateTime, nullable=False, default=func.now(), comment="创建时间")
    update_time = Column("update_time", DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment="更新时间")
    is_delete = Column("is_delete", SmallInteger, nullable=False, default=0, comment="是否删除")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_account": self.user_account,
            "user_name": self.user_name,
            "user_avatar": self.user_avatar,
            "user_profile": self.user_profile,
            "user_role": self.user_role,
            "quota": self.quota,
            "vip_time": self.vip_time.isoformat() if self.vip_time else None,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }
