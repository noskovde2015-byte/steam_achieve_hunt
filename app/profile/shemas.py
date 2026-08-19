from pydantic import BaseModel


class ProfileResponse(BaseModel):
    username: str | None
    avatar_url: str | None
    total_points: int
    platinum_count: int
