"""add weekly goal selection

Revision ID: c824b0a29a10
Revises: b36888f7a748
"""
from alembic import op
import sqlalchemy as sa

revision = "c824b0a29a10"
down_revision = "b36888f7a748"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("weekly_goals") as batch_op:
        batch_op.add_column(sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table("weekly_goals") as batch_op:
        batch_op.drop_column("selected")
