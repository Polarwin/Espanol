"""add user state quiz passed

Revision ID: b4e8c2a71d05
Revises: a3f5c1d9e7b2
"""
from alembic import op
import sqlalchemy as sa

revision = "b4e8c2a71d05"
down_revision = "a3f5c1d9e7b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user_state") as batch_op:
        batch_op.add_column(sa.Column("quiz_passed", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table("user_state") as batch_op:
        batch_op.drop_column("quiz_passed")
