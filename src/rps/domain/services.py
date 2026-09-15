from uuid import UUID

from rps.domain.entities import Game, HallOfFameEntry, Player, PlayerStats
from rps.domain.exceptions import GameNotFoundError, PlayerNotFoundError
from rps.domain.repositories import GameRepository, PlayerRepository
from rps.domain.rules import Move, random_move, resolve_round


class PlayerService:
    def __init__(self, players: PlayerRepository) -> None:
        self._players = players

    def register(self, name: str) -> Player:
        # L'unicité du nom (D1) est garantie par la contrainte UNIQUE en
        # base ; le repository lève PlayerNameConflictError en cas de
        # violation, ce qui évite une course entre un check et l'insert.
        return self._players.create(name)

    def get(self, player_id: UUID) -> Player:
        player = self._players.get(player_id)
        if player is None:
            raise PlayerNotFoundError(str(player_id))
        return player


class GameService:
    def __init__(self, players: PlayerRepository, games: GameRepository) -> None:
        self._players = players
        self._games = games

    def play(self, player_id: UUID, player_move: Move) -> Game:
        self._ensure_player_exists(player_id)
        opponent_move = random_move()
        result = resolve_round(player_move, opponent_move)
        return self._games.create(player_id, player_move, opponent_move, result)

    def get(self, game_id: UUID) -> Game:
        game = self._games.get(game_id)
        if game is None:
            raise GameNotFoundError(str(game_id))
        return game

    def list_for_player(self, player_id: UUID, limit: int, offset: int) -> tuple[list[Game], int]:
        self._ensure_player_exists(player_id)
        return self._games.list_for_player(player_id, limit, offset)

    def stats_for_player(self, player_id: UUID) -> PlayerStats:
        self._ensure_player_exists(player_id)
        return self._games.stats_for_player(player_id)

    def _ensure_player_exists(self, player_id: UUID) -> None:
        if self._players.get(player_id) is None:
            raise PlayerNotFoundError(str(player_id))


class HallOfFameService:
    def __init__(self, players: PlayerRepository, games: GameRepository) -> None:
        self._players = players
        self._games = games

    def get_ranking(self) -> list[HallOfFameEntry]:
        players = self._players.list_all()
        stats_by_player = self._games.stats_for_all_players()
        empty_stats = PlayerStats(games_played=0, wins=0, losses=0, draws=0)
        entries = [
            self._to_entry(player, stats_by_player.get(player.id, empty_stats))
            for player in players
        ]
        return sorted(entries, key=lambda entry: entry.win_rate, reverse=True)

    @staticmethod
    def _to_entry(player: Player, stats: PlayerStats) -> HallOfFameEntry:
        win_rate = round(stats.wins / stats.games_played * 100) if stats.games_played else 0
        return HallOfFameEntry(
            name=player.name,
            wins=stats.wins,
            losses=stats.losses,
            total=stats.games_played,
            win_rate=win_rate,
            created_at=player.created_at,
        )
