from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.models.user import User
from app.core.models.game import Game
from app.core.models.user_game import UserGame


async def get_profile(steam_id: str, session: AsyncSession) -> dict | None:
    stmt = select(User).where(User.steam_id == steam_id)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()
    if user is None:
        return None

    return {
        "username": user.username,
        "avatar_url": user.avatar_url,
        "total_points": user.total_points,
        "platinum_count": user.platinum_count,
    }


async def get_games(steam_id: str, session: AsyncSession):
    stmt = select(User).where(User.steam_id == steam_id)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()
    if user is None:
        return None

    user_game_stmt = (
        select(UserGame, Game)
        .join(Game, UserGame.game_id == Game.id)
        .where(UserGame.user_id == user.id)
        .order_by(UserGame.is_platinum.desc(), UserGame.achievements_unlocked.desc())
    )
    res = await session.execute(user_game_stmt)
    games = res.all()

    result = []
    for user_game, game in games:
        result.append(
            {
                "game_name": game.name,
                "total_achievements": game.total_achievements,
                "achievements_unlocked": user_game.achievements_unlocked,
                "is_platinum": user_game.is_platinum,
                "platinum_at": user_game.platinum_at,
            }
        )

    return result
