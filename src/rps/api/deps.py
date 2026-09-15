from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from rps.db.base import get_db
from rps.db.repository import SqlGameRepository, SqlPlayerRepository
from rps.domain.services import GameService, HallOfFameService, PlayerService

DbSession = Annotated[Session, Depends(get_db)]


def get_player_service(db: DbSession) -> PlayerService:
    return PlayerService(SqlPlayerRepository(db))


def get_game_service(db: DbSession) -> GameService:
    return GameService(SqlPlayerRepository(db), SqlGameRepository(db))


def get_hall_of_fame_service(db: DbSession) -> HallOfFameService:
    return HallOfFameService(SqlPlayerRepository(db), SqlGameRepository(db))
