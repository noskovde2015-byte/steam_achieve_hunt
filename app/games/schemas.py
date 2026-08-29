from pydantic import BaseModel


class GameCatalogEntry(BaseModel):
    name: str
    appid: int
    max_points: int


class GamesCatalogResponse(BaseModel):
    games: list[GameCatalogEntry]
    total: int
