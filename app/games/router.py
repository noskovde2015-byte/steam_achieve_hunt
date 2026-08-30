from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from .games_catalog_service import get_games_catalog, get_game_details
from .schemas import GamesCatalogResponse, GameDetailsResponse
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


@router.get("/{appid}", response_model=GameDetailsResponse)
async def get_game_details_router(
    appid: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    game = await get_game_details(appid=appid, session=session)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game
