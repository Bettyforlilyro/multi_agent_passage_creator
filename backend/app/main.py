"""FastAPI 主应用入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import all_routers
from app.common.exceptions import BusinessException, business_exception_handler, global_exception_handler
from app.core.lifespan import lifespan


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    fastapi_app = FastAPI(
        title="AI 爆款文章创作器",
        description="基于多智能体编排的 AI 文章创作平台",
        version="0.0.1",
        lifespan=lifespan,
    )
    # CORS 配置
    fastapi_app.add_middleware(
        CORSMiddleware,     # type: ignore
        allow_origins=["http://localhost:5173"],  # 前端开发服务器地址
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 注册路由
    for router in all_routers:
        fastapi_app.include_router(router, prefix="/api")
    # 注册全局异常处理
    fastapi_app.add_exception_handler(BusinessException, business_exception_handler)    # type: ignore
    fastapi_app.add_exception_handler(Exception, global_exception_handler)
    return fastapi_app


app = create_app()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI 爆款文章创作器 - Python 后端",
        "version": "0.0.1",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
    )
