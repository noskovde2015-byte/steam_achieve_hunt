import httpx
from app.core.config import settings


async def get_owned_games(steam_id: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/",
            params={
                "steamid": steam_id,
                "key": settings.steam.api_key,
                "include_appinfo": 1,
            },
        )

    data = response.json()
    return data["response"]["games"]
