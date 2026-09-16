"""Account-owned state for the A2 Unit 1 pilot."""
from alembic import op
import sqlalchemy as sa

revision = 'h4f9a7c3d5e1'
down_revision = 'g3e8d6a2b4c0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('a2_sample_progress',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('data', sa.JSON(), nullable=False))


def downgrade():
    op.drop_table('a2_sample_progress')
