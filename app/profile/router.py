from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from app.core.models.user import User
from app.core.models.db_helper import db_helper
from .profile_service import get_profile, get_games
from .schemas import ProfileResponse, UserGameResponse

router = APIRouter(prefix=settings.api_prefix.profile_prefix, tags=["Profile"])


@router.get("/{steam_id}", response_model=ProfileResponse)
async def get_user_profile(
    steam_id: str, session: AsyncSession = Depends(db_helper.session_getter)
):
    user = await get_profile(steam_id=steam_id, session=session)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{steam_id}/games", response_model=list[UserGameResponse])
async def get_user_games(
    steam_id: str, session: AsyncSession = Depends(db_helper.session_getter)
):
    games = await get_games(steam_id=steam_id, session=session)
    if games is None:
        raise HTTPException(status_code=404, detail="User not found")
    return games
