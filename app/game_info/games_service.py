import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.user_game import UserGame
from app.core.models.user import User
from app.core.config import settings


async def get_owned_games(steam_id: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/",
            params={
                "steamid": steam_id,
                "key": settings.steam.api_key,
                "include_appinfo": 1,
            },
        )

    data = response.json()
    return data["response"]["games"]


async def get_player_achievements(steam_id: str, appid: int) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/",
            params={
                "steamid": steam_id,
                "appid": appid,
                "key": settings.steam.api_key,
            },
        )
    data = response.json()
    return data["playerstats"]["achievements"]


async def get_schema_for_game(appid: int) -> int:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/",
            params={
                "appid": appid,
                "key": settings.steam.api_key,
            },
        )

    data = response.json()
    achievements = data["game"]["availableGameStats"].get("achievements", [])
    return len(achievements)


async def sync_user_game(user_id: int, appid: int, session: AsyncSession) -> UserGame:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one()

    user_achievements = await get_player_achievements(
        steam_id=user.steam_id, appid=appid
    )

    game_achievements = await get_schema_for_game(appid=appid)
