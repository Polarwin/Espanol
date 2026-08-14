"""add user nickname

Revision ID: e1c6b4a8d2f0
Revises: d94052bc9b82
"""
from alembic import op
import sqlalchemy as sa

revision = "e1c6b4a8d2f0"
down_revision = "d94052bc9b82"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("nickname", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("nickname")
