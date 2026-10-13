from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------- 启动阶段 ----------
    # 1. 创建异步数据库引擎（连接池在此初始化）
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,   # 连接前 ping 一下，自动剔除失效连接
    )
    # 2. 创建会话工厂，绑定到 engine
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    # 3. 创建 Redis 异步客户端
    redis_client = Redis.from_url(settings.redis_url, encoding='utf-8', decode_responses=True)

    # 4. 把资源挂到 app.state，供依赖注入读取
    app.state.engine = engine   # type: ignore
    app.state.session_factory = session_factory   # type: ignore
    app.state.redis = redis_client   # type: ignore
    print(f"数据库连接成功: {settings.database_url}")
    print(f"Redis 连接成功: {settings.redis_url}")

    yield

    # ---------- 关闭阶段 ----------
    await redis_client.aclose()
    await engine.dispose()
    print("应用已关闭，资源已释放。")
