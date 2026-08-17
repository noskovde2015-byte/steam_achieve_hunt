from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.refresh_token import RefreshToken
from app.core.models.user import User
from app.core.config import settings
import secrets
import hashlib


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.auth.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm
    )


def verify_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token, settings.auth.secret_key, algorithms=[settings.auth.algorithm]
        )
    except JWTError:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None
    return int(user_id)


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def save_refresh_token(user_id: int, token: str, session: AsyncSession) -> None:
    token_hash = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.auth.refresh_token_expire_days
    )

    stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
    result = await session.execute(stmt)
    refresh_token = result.scalar_one_or_none()

    if refresh_token is None:
        refresh_token = RefreshToken(user_id=user_id)
        session.add(refresh_token)

    refresh_token.token_hash = token_hash
    refresh_token.expires_at = expires_at

    await session.commit()


async def verify_refresh_token(token: str, session: AsyncSession) -> User | None:
    token_hash = hash_token(token)

    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await session.execute(stmt)
    refresh_token = result.scalar_one_or_none()

    if refresh_token is None:
        return None
    if refresh_token.expires_at < datetime.now(timezone.utc):
        return None

    user_stmt = select(User).where(User.id == refresh_token.user_id)
    user_result = await session.execute(user_stmt)
    return user_result.scalar_one_or_none()
