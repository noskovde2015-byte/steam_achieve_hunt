from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.game import Game
from app.core.models.achievements import Achievement


async def get_games_catalog(
    session: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[dict], int]:
    points_formula = func.coalesce(
        func.sum(func.least(100, 100 / func.nullif(Achievement.global_percent, 0))), 0
    )

    stmt = (
        select(
            Game,
            points_formula.label("max_points"),
        )
        .outerjoin(Achievement, Achievement.game_id == Game.id)
        .group_by(Game.id)
        .order_by(points_formula.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    result = await session.execute(stmt)
    rows = result.all()

    games = [
        {"name": game.name, "appid": game.appid, "max_points": round(max_points)}
        for game, max_points in rows
    ]

    count_stmt = select(func.count(Game.id))
    total = (await session.execute(count_stmt)).scalar_one()

    return games, total
