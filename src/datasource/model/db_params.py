from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func


def define_models(db):
    """Создание классов, представляющих таблицы в БД"""
    class Players(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        login: Mapped[str] = mapped_column(unique=True, nullable=False)
        password: Mapped[str] = mapped_column(nullable=False)
        uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False, server_default=func.gen_random_uuid())

    class Profiles(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        username: Mapped[str] = mapped_column(unique=True, nullable=False)
        email: Mapped[str] = mapped_column(unique=True, nullable=False)
        player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
        player: Mapped["Players"] = relationship("Players", foreign_keys=[player_id])

    class SavedGames(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
        game_uuid: Mapped[str] = mapped_column(unique=True, nullable=False)
        board: Mapped[str] = mapped_column(nullable=False)
        game_status: Mapped[int] = mapped_column(nullable=True)
        player_owner_uuid: Mapped[str] = mapped_column(ForeignKey("players.uuid"), nullable=True)
        player_owner: Mapped["Players"] = relationship("Players", foreign_keys=[player_owner_uuid])
        player_guest_uuid: Mapped[str] = mapped_column(ForeignKey("players.uuid"), nullable=True)
        player_guest: Mapped["Players"] = relationship("Players", foreign_keys=[player_guest_uuid])
        game_type: Mapped[int] = mapped_column(nullable=True)

    return Players, Profiles, SavedGames


