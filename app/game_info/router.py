import httpx
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.core.config import settings
from .games_service import sync_all_user_games
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.db_helper import db_helper
from app.messaging.rabbitmq import publish_sync_task

router = APIRouter(prefix=settings.api_prefix.sync_prefix, tags=["Sync"])


@router.post("/")
async def sync_games(user=Depends(get_current_user)):
    await publish_sync_task(user_id=user.id)
    return {"detail": "Синхронизация запущена"}
