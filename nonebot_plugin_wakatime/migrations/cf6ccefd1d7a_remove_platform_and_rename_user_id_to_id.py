"""remove platform and rename user_id to id

迁移 ID: cf6ccefd1d7a
父迁移:
创建时间: 2024-08-01 08:58:54.835575

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "cf6ccefd1d7a"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = ("wakatime",)
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("wakatime", schema=None) as batch_op:
        batch_op.add_column(sa.Column("id", sa.String(), nullable=False))
        batch_op.drop_column("user_id")
        batch_op.drop_column("platform")

    # ### end Alembic commands ###


def downgrade(name: str = "") -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("wakatime", schema=None) as batch_op:
        batch_op.add_column(sa.Column("platform", sa.VARCHAR(), nullable=False))
        batch_op.add_column(sa.Column("user_id", sa.VARCHAR(), nullable=False))
        batch_op.drop_column("id")

    # ### end Alembic commands ###