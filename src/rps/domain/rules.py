import random
from enum import StrEnum


class Move(StrEnum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


class Result(StrEnum):
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"


# Move -> le coup qu'il bat.
_BEATS: dict[Move, Move] = {
    Move.ROCK: Move.SCISSORS,
    Move.SCISSORS: Move.PAPER,
    Move.PAPER: Move.ROCK,
}


def resolve_round(player_move: Move, opponent_move: Move) -> Result:
    if player_move == opponent_move:
        return Result.DRAW
    if _BEATS[player_move] == opponent_move:
        return Result.WIN
    return Result.LOSS


def random_move() -> Move:
    return random.choice(list(Move))
