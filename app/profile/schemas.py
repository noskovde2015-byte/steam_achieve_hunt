from datetime import datetime

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    username: str | None
    avatar_url: str | None
    total_points: int
    platinum_count: int


class UserGameResponse(BaseModel):
    game_name: str
    total_achievements: int
    achievements_unlocked: int
    is_platinum: bool
    platinum_at: datetime | None
