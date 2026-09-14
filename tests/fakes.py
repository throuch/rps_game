import uuid
from datetime import UTC, datetime

from rps.domain.entities import Game, Player, PlayerStats
from rps.domain.exceptions import PlayerNameConflictError
from rps.domain.rules import Move, Result


class FakePlayerRepository:
    def __init__(self) -> None:
        self._by_id: dict[uuid.UUID, Player] = {}

    def create(self, name: str) -> Player:
        if self.get_by_name(name) is not None:
            raise PlayerNameConflictError(name)
        player = Player(id=uuid.uuid4(), name=name, created_at=datetime.now(UTC))
        self._by_id[player.id] = player
        return player

    def get(self, player_id: uuid.UUID) -> Player | None:
        return self._by_id.get(player_id)

    def get_by_name(self, name: str) -> Player | None:
        return next((p for p in self._by_id.values() if p.name == name), None)


class FakeGameRepository:
    def __init__(self) -> None:
        self._games: dict[uuid.UUID, Game] = {}

    def create(
        self, player_id: uuid.UUID, player_move: Move, opponent_move: Move, result: Result
    ) -> Game:
        game = Game(
            id=uuid.uuid4(),
            player_id=player_id,
            player_move=player_move,
            opponent_move=opponent_move,
            result=result,
            created_at=datetime.now(UTC),
        )
        self._games[game.id] = game
        return game

    def get(self, game_id: uuid.UUID) -> Game | None:
        return self._games.get(game_id)

    def list_for_player(
        self, player_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Game], int]:
        games = sorted(
            (g for g in self._games.values() if g.player_id == player_id),
            key=lambda g: g.created_at,
            reverse=True,
        )
        return games[offset : offset + limit], len(games)

    def stats_for_player(self, player_id: uuid.UUID) -> PlayerStats:
        games = [g for g in self._games.values() if g.player_id == player_id]
        wins = sum(1 for g in games if g.result is Result.WIN)
        losses = sum(1 for g in games if g.result is Result.LOSS)
        draws = sum(1 for g in games if g.result is Result.DRAW)
        return PlayerStats(games_played=len(games), wins=wins, losses=losses, draws=draws)
