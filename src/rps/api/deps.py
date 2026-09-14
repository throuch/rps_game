from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from rps.db.base import get_db
from rps.db.repository import SqlGameRepository, SqlPlayerRepository
from rps.domain.services import GameService, PlayerService

DbSession = Annotated[Session, Depends(get_db)]


def get_player_service(db: DbSession) -> PlayerService:
    return PlayerService(SqlPlayerRepository(db))


def get_game_service(db: DbSession) -> GameService:
    return GameService(SqlPlayerRepository(db), SqlGameRepository(db))
