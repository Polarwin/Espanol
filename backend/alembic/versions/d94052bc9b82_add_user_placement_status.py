"""add user placement status

Revision ID: d94052bc9b82
Revises: c824b0a29a10
"""
from alembic import op
import sqlalchemy as sa

revision = "d94052bc9b82"
down_revision = "c824b0a29a10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("placement_completed", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("placement_completed")
