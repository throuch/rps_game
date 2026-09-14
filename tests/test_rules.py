import pytest

from rps.domain.rules import Move, Result, resolve_round


@pytest.mark.parametrize(
    ("player_move", "opponent_move", "expected"),
    [
        (Move.ROCK, Move.SCISSORS, Result.WIN),
        (Move.SCISSORS, Move.PAPER, Result.WIN),
        (Move.PAPER, Move.ROCK, Result.WIN),
        (Move.ROCK, Move.PAPER, Result.LOSS),
        (Move.PAPER, Move.SCISSORS, Result.LOSS),
        (Move.SCISSORS, Move.ROCK, Result.LOSS),
        (Move.ROCK, Move.ROCK, Result.DRAW),
        (Move.PAPER, Move.PAPER, Result.DRAW),
        (Move.SCISSORS, Move.SCISSORS, Result.DRAW),
    ],
)
def test_resolve_round(player_move: Move, opponent_move: Move, expected: Result) -> None:
    assert resolve_round(player_move, opponent_move) is expected
