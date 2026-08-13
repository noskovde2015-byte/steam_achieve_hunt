from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserGame(Base):
    __tablename__ = "user_games"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    achievements_unlocked: Mapped[int] = mapped_column(default=0)
    is_platinum: Mapped[bool] = mapped_column(default=False)
    points_earned: Mapped[int] = mapped_column(default=0)
    platinum_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(nullable=True)
