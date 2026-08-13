from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from core.models import User
from urllib.parse import urlencode
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.core.config import settings
import json


def build_steam_login_url(return_to: str, realm: str) -> str:
    steam_openid_url = "https://steamcommunity.com/openid/login"

    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": return_to,
        "openid.realm": realm,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }

    return f"{steam_openid_url}?{urlencode(params)}"


async def verify_steam_response(params: dict) -> str | None:
    params["openid.mode"] = "check_authentication"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://steamcommunity.com/openid/login", data=params
        )

    if "is_valid:true" in response.text:
        parsed = params["openid.claimed_id"]
        user_id = parsed.split("/")[-1]
        return user_id
    else:
        return None


async def get_player_summary(steam_id: str) -> dict:

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/",
            params={"steamids": steam_id, "key": settings.steam.api_key},
        )
    data = response.json()
    return data["response"]["players"][0]


async def get_or_create_user(steam_id: str, session: AsyncSession) -> User:
    stmt = select(User).where(User.steam_id == steam_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    user_info = await get_player_summary(steam_id=steam_id)

    if user is None:
        user = User(steam_id=steam_id)
        session.add(user)

    user.username = user_info["personaname"]
    user.avatar_url = user_info["avatarfull"]

    await session.commit()
    await session.refresh(user)
    return user
