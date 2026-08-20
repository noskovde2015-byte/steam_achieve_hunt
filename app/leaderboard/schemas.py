from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    username: str | None
    avatar_url: str | None
    platinum_count: int
    total_points: int
