from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, join
from app.core.models.user import User
from app.core.models.user_game import UserGame


async def get_leaderboard(session: AsyncSession, limit: int = 100) -> list[User]:
    stmt = select(User).order_by(User.platinum_count.desc()).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_monthly_leaderboard(session: AsyncSession, limit: int = 100):
    month_start = datetime.now(timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )

    stmt = (
        select(User, func.count(UserGame.id).label("platinum_count"))
        .join(UserGame, UserGame.user_id == User.id)
        .where(UserGame.is_platinum == True, UserGame.platinum_at >= month_start)
        .group_by(User.id)
        .order_by(func.count(UserGame.id).desc())
        .limit(limit)
    )
    result = await session.execute(stmt)

    return [
        {
            "username": user.username,
            "avatar_url": user.avatar_url,
            "platinum_count": count,
            "total_points": 0,
        }
        for user, count in result
    ]
