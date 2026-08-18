from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.core.config import settings
from .games_service import sync_all_user_games
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.db_helper import db_helper

router = APIRouter(prefix=settings.api_prefix.sync_prefix, tags=["Sync"])


@router.post("/")
async def sync_games(
    user=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await sync_all_user_games(session=session, user_id=user.id)
