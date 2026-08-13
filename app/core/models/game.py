from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Game(Base):
    __tablename__ = "games"
    appid: Mapped[int] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    total_achievements: Mapped[int] = mapped_column(default=0)
