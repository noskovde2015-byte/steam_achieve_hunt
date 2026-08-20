from fastapi import APIRouter

from app.core.config import settings
from app.auth.router import router as auth_router
from app.game_info.router import router as game_info_router
from app.profile.router import router as profile_router
from app.leaderboard.router import router as leaderboard_router

api_router = APIRouter(prefix=settings.api_prefix.prefix)
api_router.include_router(auth_router)
api_router.include_router(game_info_router)
api_router.include_router(profile_router)
api_router.include_router(leaderboard_router)
