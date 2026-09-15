from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from rps.domain.rules import Move, Result


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class PlayerStatsResponse(BaseModel):
    games_played: int
    wins: int
    losses: int
    draws: int


class PlayerResponse(BaseModel):
    player_id: UUID
    name: str
    created_at: datetime


class PlayerDetailResponse(PlayerResponse):
    stats: PlayerStatsResponse


class PlayRequest(BaseModel):
    player_id: UUID
    move: Move


class GameResponse(BaseModel):
    game_id: UUID
    player_move: Move
    opponent_move: Move
    result: Result
    created_at: datetime


class GameDetailResponse(GameResponse):
    player_id: UUID


class GameListResponse(BaseModel):
    items: list[GameResponse]
    total: int


class HallOfFameEntryResponse(BaseModel):
    name: str
    wins: int
    losses: int
    total: int
    win_rate: int
    created_at: datetime


class HallOfFameResponse(BaseModel):
    items: list[HallOfFameEntryResponse]
