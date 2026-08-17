from fastapi import APIRouter, Depends, HTTPException, Request, Response

from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.db_helper import db_helper
from app.auth.steam_service import (
    build_steam_login_url,
    verify_steam_response,
    get_or_create_user,
)
from app.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    save_refresh_token,
    verify_access_token,
    verify_refresh_token,
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
    request: Request,
    response: Response,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    params = dict(request.query_params)
    steam_id = await verify_steam_response(params)

    if steam_id is None:
        raise HTTPException(status_code=404, detail="Steam login failed")

    user = await get_or_create_user(session=session, steam_id=steam_id)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token()
    await save_refresh_token(user_id=user.id, token=refresh_token, session=session)

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite="lax",
        max_age=settings.auth.access_token_expire_minutes * 60,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        samesite="lax",
        path="/api/auth/refresh",
        max_age=settings.auth.refresh_token_expire_days * 24 * 60 * 60,
    )

    return {
        "steam_id": steam_id,
        "username": user.username,
        "avatar_url": user.avatar_url,
    }


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    old_refresh_token = request.cookies.get("refresh_token")
    if old_refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    user = await verify_refresh_token(token=old_refresh_token, session=session)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token()
    await save_refresh_token(user_id=user.id, token=new_refresh_token, session=session)

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite="lax",
        max_age=settings.auth.access_token_expire_minutes * 60,
    )
    response.set_cookie(
        "refresh_token",
        new_refresh_token,
        httponly=True,
        samesite="lax",
        path="/api/auth/refresh",
        max_age=settings.auth.refresh_token_expire_days * 24 * 60 * 60,
    )

    return {"detail": "Token refreshed"}
