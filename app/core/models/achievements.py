from datetime import datetime

from sqlalchemy import ForeignKey, String, Float, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = (
        UniqueConstraint("game_id", "api_name", name="uq_game_achievement"),
    )
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    api_name: Mapped[str] = mapped_column(String)
    global_percent: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
