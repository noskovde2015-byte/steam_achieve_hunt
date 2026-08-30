from pydantic import BaseModel


class GameCatalogEntry(BaseModel):
    name: str
    appid: int
    max_points: int


class GamesCatalogResponse(BaseModel):
    games: list[GameCatalogEntry]
    total: int


class GameDetailsResponse(BaseModel):
    name: str
    total_achievements: int
    max_points: int
