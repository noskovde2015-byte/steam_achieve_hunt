from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.user_game import UserGame
from app.core.models.user import User
from app.core.models.game import Game
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


async def get_schema_for_game(appid: int) -> tuple[str, int]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/",
            params={
                "appid": appid,
                "key": settings.steam.api_key,
            },
        )

    data = response.json()
    game_name = data["game"]["gameName"]
    achievements = data["game"]["availableGameStats"].get("achievements", [])
    return game_name, len(achievements)


async def sync_user_game(user_id: int, appid: int, session: AsyncSession) -> UserGame:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one()

    user_achievements = await get_player_achievements(
        steam_id=user.steam_id, appid=appid
    )
    game_name, total_achievements = await get_schema_for_game(appid=appid)

    unlocked_count = sum(1 for a in user_achievements if a["achieved"] == 1)
    is_platinum = total_achievements > 0 and unlocked_count == total_achievements

    platinum_time = None
    if is_platinum:
        platinum_timestamp = max(
            a["unlocktime"] for a in user_achievements if a["achieved"] == 1
        )
        platinum_time = datetime.fromtimestamp(
            platinum_timestamp, tz=timezone.utc
        ).replace(tzinfo=None)

    game_stmt = select(Game).where(Game.appid == appid)
    game_result = await session.execute(game_stmt)
    game = game_result.scalar_one_or_none()

    if game is None:
        game = Game(appid=appid, name=game_name, total_achievements=total_achievements)
        session.add(game)
        await session.flush()
    else:
        game.name = game_name
        game.total_achievements = total_achievements

    user_game_stmt = select(UserGame).where(
        UserGame.user_id == user_id, UserGame.game_id == game.id
    )
    user_game_result = await session.execute(user_game_stmt)
    user_game = user_game_result.scalar_one_or_none()

    if user_game is None:
        user_game = UserGame(user_id=user_id, game_id=game.id)
        session.add(user_game)

    user_game.achievements_unlocked = unlocked_count
    user_game.is_platinum = is_platinum
    user_game.platinum_at = platinum_time
    user_game.last_synced_at = datetime.now(timezone.utc).replace(tzinfo=None)

    await session.commit()
    await session.refresh(user_game)

    return user_game
