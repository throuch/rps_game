import uuid

import pytest

from rps.domain.exceptions import GameNotFoundError, PlayerNameConflictError, PlayerNotFoundError
from rps.domain.rules import Move
from rps.domain.services import GameService, PlayerService

from .fakes import FakeGameRepository, FakePlayerRepository


@pytest.fixture
def player_repo() -> FakePlayerRepository:
    return FakePlayerRepository()


@pytest.fixture
def game_repo() -> FakeGameRepository:
    return FakeGameRepository()


@pytest.fixture
def player_service(player_repo: FakePlayerRepository) -> PlayerService:
    return PlayerService(player_repo)


@pytest.fixture
def game_service(
    player_repo: FakePlayerRepository, game_repo: FakeGameRepository
) -> GameService:
    return GameService(player_repo, game_repo)


def test_register_creates_player(player_service: PlayerService) -> None:
    player = player_service.register("Thomas")
    assert player.name == "Thomas"


def test_register_duplicate_name_raises_conflict(player_service: PlayerService) -> None:
    player_service.register("Thomas")
    with pytest.raises(PlayerNameConflictError):
        player_service.register("Thomas")


def test_get_unknown_player_raises_not_found(player_service: PlayerService) -> None:
    with pytest.raises(PlayerNotFoundError):
        player_service.get(uuid.uuid4())


def test_play_unknown_player_raises_not_found(game_service: GameService) -> None:
    with pytest.raises(PlayerNotFoundError):
        game_service.play(uuid.uuid4(), Move.ROCK)


def test_play_persists_a_game_for_existing_player(
    player_service: PlayerService, game_service: GameService
) -> None:
    player = player_service.register("Thomas")
    game = game_service.play(player.id, Move.ROCK)
    assert game.player_id == player.id
    assert game.player_move is Move.ROCK


def test_get_unknown_game_raises_not_found(game_service: GameService) -> None:
    with pytest.raises(GameNotFoundError):
        game_service.get(uuid.uuid4())


def test_stats_for_player_aggregates_results(
    player_service: PlayerService, game_service: GameService, monkeypatch: pytest.MonkeyPatch
) -> None:
    player = player_service.register("Thomas")
    # Coup adverse forcé pour rendre le test déterministe.
    monkeypatch.setattr("rps.domain.services.random_move", lambda: Move.SCISSORS)
    game_service.play(player.id, Move.ROCK)  # rock bat scissors -> win
    game_service.play(player.id, Move.SCISSORS)  # scissors == scissors -> draw
    stats = game_service.stats_for_player(player.id)
    assert stats.games_played == 2
    assert stats.wins == 1
    assert stats.draws == 1
    assert stats.losses == 0


def test_list_for_player_paginates(
    player_service: PlayerService, game_service: GameService, monkeypatch: pytest.MonkeyPatch
) -> None:
    player = player_service.register("Thomas")
    monkeypatch.setattr("rps.domain.services.random_move", lambda: Move.SCISSORS)
    for _ in range(3):
        game_service.play(player.id, Move.ROCK)
    games, total = game_service.list_for_player(player.id, limit=2, offset=0)
    assert total == 3
    assert len(games) == 2


def test_list_for_player_unknown_player_raises_not_found(game_service: GameService) -> None:
    with pytest.raises(PlayerNotFoundError):
        game_service.list_for_player(uuid.uuid4(), limit=20, offset=0)
