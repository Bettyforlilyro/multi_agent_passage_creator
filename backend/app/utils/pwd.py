""" 密码加密工具 """
import hashlib
from app.core.config import settings


def encrypt_password(password: str) -> str:
    """ 加密密码，使用md5+盐值 """
    return hashlib.md5((password + settings.password_salt).encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ 验证密码是否匹配 """
    # 对比明文密码和加密后的密码是否一致
    return encrypt_password(plain_password) == hashed_password
