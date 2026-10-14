"""API 路由"""

from app.api.health import router as health_router
from app.api.user import router as user_router

all_routers = [
    health_router,
    user_router,
]
