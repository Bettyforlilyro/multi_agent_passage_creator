"""API 路由"""

from app.api.health import router as health_router

all_routers = [
    health_router,
]
