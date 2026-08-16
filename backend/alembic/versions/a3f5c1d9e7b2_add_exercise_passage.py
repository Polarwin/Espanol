"""add exercise passage for reading

Revision ID: a3f5c1d9e7b2
Revises: f2d7c5b9e3a1
"""
from alembic import op
import sqlalchemy as sa

revision = "a3f5c1d9e7b2"
down_revision = "f2d7c5b9e3a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("exercises") as batch_op:
        batch_op.add_column(sa.Column("passage", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("exercises") as batch_op:
        batch_op.drop_column("passage")
