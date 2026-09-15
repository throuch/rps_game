import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rps.db.models import GameModel, PlayerModel
from rps.domain.entities import Game, Player, PlayerStats
from rps.domain.exceptions import PlayerNameConflictError
from rps.domain.rules import Move, Result


def _to_player(model: PlayerModel) -> Player:
    return Player(id=model.id, name=model.name, created_at=model.created_at)


def _to_game(model: GameModel) -> Game:
    return Game(
        id=model.id,
        player_id=model.player_id,
        player_move=Move(model.player_move),
        opponent_move=Move(model.opponent_move),
        result=Result(model.result),
        created_at=model.created_at,
    )


class SqlPlayerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, name: str) -> Player:
        model = PlayerModel(name=name)
        self._session.add(model)
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise PlayerNameConflictError(name) from exc
        return _to_player(model)

    def get(self, player_id: uuid.UUID) -> Player | None:
        model = self._session.get(PlayerModel, player_id)
        return _to_player(model) if model else None

    def get_by_name(self, name: str) -> Player | None:
        model = self._session.scalar(select(PlayerModel).where(PlayerModel.name == name))
        return _to_player(model) if model else None

    def list_all(self) -> list[Player]:
        models = self._session.scalars(select(PlayerModel))
        return [_to_player(model) for model in models]


class SqlGameRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self, player_id: uuid.UUID, player_move: Move, opponent_move: Move, result: Result
    ) -> Game:
        model = GameModel(
            player_id=player_id,
            player_move=player_move.value,
            opponent_move=opponent_move.value,
            result=result.value,
        )
        self._session.add(model)
        self._session.commit()
        return _to_game(model)

    def get(self, game_id: uuid.UUID) -> Game | None:
        model = self._session.get(GameModel, game_id)
        return _to_game(model) if model else None

    def list_for_player(
        self, player_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Game], int]:
        total = self._session.scalar(
            select(func.count()).select_from(GameModel).where(GameModel.player_id == player_id)
        )
        rows = self._session.scalars(
            select(GameModel)
            .where(GameModel.player_id == player_id)
            .order_by(GameModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_game(row) for row in rows], total or 0

    def stats_for_player(self, player_id: uuid.UUID) -> PlayerStats:
        rows = self._session.execute(
            select(GameModel.result, func.count())
            .where(GameModel.player_id == player_id)
            .group_by(GameModel.result)
        ).all()
        counts = dict(rows)
        wins = counts.get(Result.WIN.value, 0)
        losses = counts.get(Result.LOSS.value, 0)
        draws = counts.get(Result.DRAW.value, 0)
        return PlayerStats(
            games_played=wins + losses + draws, wins=wins, losses=losses, draws=draws
        )

    def stats_for_all_players(self) -> dict[uuid.UUID, PlayerStats]:
        rows = self._session.execute(
            select(GameModel.player_id, GameModel.result, func.count()).group_by(
                GameModel.player_id, GameModel.result
            )
        ).all()
        counts: dict[uuid.UUID, dict[str, int]] = {}
        for player_id, result, count in rows:
            counts.setdefault(player_id, {})[result] = count
        return {
            player_id: PlayerStats(
                games_played=sum(result_counts.values()),
                wins=result_counts.get(Result.WIN.value, 0),
                losses=result_counts.get(Result.LOSS.value, 0),
                draws=result_counts.get(Result.DRAW.value, 0),
            )
            for player_id, result_counts in counts.items()
        }
