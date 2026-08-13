from fastapi import APIRouter, Depends, HTTPException, Request

from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.db_helper import db_helper
from app.auth.steam_service import (
    build_steam_login_url,
    verify_steam_response,
    get_or_create_user,
)
from app.core.config import settings

router = APIRouter(prefix=settings.api_prefix.auth_prefix, tags=["Auth"])


@router.get("/steam/login")
async def steam_login(request: Request):
    url = build_steam_login_url(
        return_to=str(request.url_for("steam_callback")), realm=str(request.base_url)
    )
    return RedirectResponse(url=url)


@router.get("/steam/callback")
async def steam_callback(
    request: Request, session: AsyncSession = Depends(db_helper.session_getter)
):
    params = dict(request.query_params)
    steam_id = await verify_steam_response(params)

    if steam_id is None:
        raise HTTPException(status_code=404, detail="Steam login failed")

    user = await get_or_create_user(session=session, steam_id=steam_id)
    return {
        "steam_id": steam_id,
        "username": user.username,
        "avatar_url": user.avatar_url,
    }
