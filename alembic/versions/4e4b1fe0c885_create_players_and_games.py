"""create players and games tables

Revision ID: 4e4b1fe0c885
Revises:
Create Date: 2026-09-14 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "4e4b1fe0c885"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "players",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("name", name="uq_players_name"),
    )

    op.create_table(
        "games",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_move", sa.String(length=8), nullable=False),
        sa.Column("opponent_move", sa.String(length=8), nullable=False),
        sa.Column("result", sa.String(length=4), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], name="fk_games_player_id"),
    )
    op.create_index("ix_games_player_id", "games", ["player_id"])


def downgrade() -> None:
    op.drop_index("ix_games_player_id", table_name="games")
    op.drop_table("games")
    op.drop_table("players")
