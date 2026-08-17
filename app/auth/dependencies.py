from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.db_helper import db_helper
from app.core.models.user import User
from app.auth.jwt_service import verify_access_token


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    access_token = request.cookies.get("access_token")

    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = verify_access_token(access_token)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
