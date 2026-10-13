"""FastAPI 主应用入口"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import all_routers
from app.common.exceptions import BusinessException, ErrorCode
from app.core.lifespan import lifespan


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    fastapi_app = FastAPI(
        title="AI 爆款文章创作器",
        description="基于多智能体编排的 AI 文章创作平台",
        version="0.0.1",
        lifespan=lifespan,
    )
    # 注册路由
    for router in all_routers:
        fastapi_app.include_router(router, prefix="/api")
    # CORS 配置
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # 前端开发服务器地址
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return fastapi_app


app = create_app()


# 全局异常处理
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理"""
    return JSONResponse(
        status_code=200,
        content={
            "code": exc.error_code.code,
            "data": None,
            "message": exc.message
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    print(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.SYSTEM_ERROR.code,
            "data": None,
            "message": f"系统内部异常: {str(exc)}"
        }
    )


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
