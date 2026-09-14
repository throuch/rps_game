from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from rps.domain.rules import Move, Result


@dataclass(frozen=True)
class Player:
    id: UUID
    name: str
    created_at: datetime


@dataclass(frozen=True)
class Game:
    id: UUID
    player_id: UUID
    player_move: Move
    opponent_move: Move
    result: Result
    created_at: datetime


@dataclass(frozen=True)
class PlayerStats:
    games_played: int
    wins: int
    losses: int
    draws: int
