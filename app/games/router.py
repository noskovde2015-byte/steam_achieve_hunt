from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from .games_catalog_service import get_games_catalog
from .schemas import GamesCatalogResponse
from app.core.models.db_helper import db_helper

router = APIRouter(prefix=settings.api_prefix.games_prefix, tags=["Games"])


@router.get("/", response_model=GamesCatalogResponse)
async def get_games_catalog_router(
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    games, total = await get_games_catalog(
        session=session, page=page, page_size=page_size
    )
    return GamesCatalogResponse(games=games, total=total)
