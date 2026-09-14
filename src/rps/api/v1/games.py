from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from rps.api.deps import get_game_service
from rps.api.schemas import GameDetailResponse, GameResponse, PlayRequest
from rps.domain.exceptions import GameNotFoundError, PlayerNotFoundError
from rps.domain.services import GameService

router = APIRouter(tags=["games"])


@router.post("/play", response_model=GameResponse, status_code=201)
def play(
    body: PlayRequest, service: Annotated[GameService, Depends(get_game_service)]
) -> GameResponse:
    try:
        game = service.play(body.player_id, body.move)
    except PlayerNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Player not found") from exc
    return GameResponse(
        game_id=game.id,
        player_move=game.player_move,
        opponent_move=game.opponent_move,
        result=game.result,
        created_at=game.created_at,
    )


@router.get("/games/{game_id}", response_model=GameDetailResponse)
def get_game(
    game_id: UUID, service: Annotated[GameService, Depends(get_game_service)]
) -> GameDetailResponse:
    try:
        game = service.get(game_id)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Game not found") from exc
    return GameDetailResponse(
        game_id=game.id,
        player_id=game.player_id,
        player_move=game.player_move,
        opponent_move=game.opponent_move,
        result=game.result,
        created_at=game.created_at,
    )
