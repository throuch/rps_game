from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from rps.api.deps import get_game_service, get_player_service
from rps.api.schemas import (
    GameListResponse,
    GameResponse,
    PlayerDetailResponse,
    PlayerResponse,
    PlayerStatsResponse,
    RegisterRequest,
)
from rps.domain.exceptions import PlayerNameConflictError, PlayerNotFoundError
from rps.domain.services import GameService, PlayerService

router = APIRouter(tags=["players"])


@router.post("/register", response_model=PlayerResponse, status_code=201)
def register(
    body: RegisterRequest, service: Annotated[PlayerService, Depends(get_player_service)]
) -> PlayerResponse:
    try:
        player = service.register(body.name)
    except PlayerNameConflictError as exc:
        raise HTTPException(status_code=409, detail="Player name already taken") from exc
    return PlayerResponse(player_id=player.id, name=player.name, created_at=player.created_at)


@router.get("/players/{player_id}", response_model=PlayerDetailResponse)
def get_player(
    player_id: UUID,
    player_service: Annotated[PlayerService, Depends(get_player_service)],
    game_service: Annotated[GameService, Depends(get_game_service)],
) -> PlayerDetailResponse:
    try:
        player = player_service.get(player_id)
        stats = game_service.stats_for_player(player_id)
    except PlayerNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Player not found") from exc
    return PlayerDetailResponse(
        player_id=player.id,
        name=player.name,
        created_at=player.created_at,
        stats=PlayerStatsResponse(
            games_played=stats.games_played,
            wins=stats.wins,
            losses=stats.losses,
            draws=stats.draws,
        ),
    )


@router.get("/players/{player_id}/games", response_model=GameListResponse)
def list_player_games(
    player_id: UUID,
    game_service: Annotated[GameService, Depends(get_game_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> GameListResponse:
    try:
        games, total = game_service.list_for_player(player_id, limit, offset)
    except PlayerNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Player not found") from exc
    items = [
        GameResponse(
            game_id=g.id,
            player_move=g.player_move,
            opponent_move=g.opponent_move,
            result=g.result,
            created_at=g.created_at,
        )
        for g in games
    ]
    return GameListResponse(items=items, total=total)
