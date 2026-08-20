from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.user import User
from app.core.models.db_helper import db_helper
from app.core.config import settings
from .schemas import LeaderboardEntry
from .leaderboard_service import get_leaderboard, get_monthly_leaderboard

router = APIRouter(prefix=settings.api_prefix.leaderboard_prefix, tags=["Leaderboard"])


@router.get("/", response_model=list[LeaderboardEntry])
async def get_all_time_leaderboards(
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_leaderboard(session=session, limit=limit)


@router.get("/monthly", response_model=list[LeaderboardEntry])
async def get_monthly_leaderboard_route(
    limit: int = 100,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_monthly_leaderboard(session=session, limit=limit)
