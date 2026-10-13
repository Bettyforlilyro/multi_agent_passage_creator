from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录（python-backend 目录）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):

    # 服务器配置
    server_port: int = 8000
    server_host: str = "0.0.0.0"

    # 数据库配置
    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str

    # Redis 配置
    redis_host: str
    redis_port: int
    redis_db: int = 0
    redis_user: str
    redis_password: str

    # Session 配置
    session_secret_key: str
    session_max_age: int = 2592000  # 30 天

    # 密码加密盐值
    password_salt: str

    # 其他配置
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """获取数据库连接 URL"""
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"

    @property
    def redis_url(self) -> str:
        """获取 Redis 连接 URL"""
        if self.redis_password:
            return f"redis://{self.redis_user}:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
