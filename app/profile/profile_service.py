from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.models.user import User


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
