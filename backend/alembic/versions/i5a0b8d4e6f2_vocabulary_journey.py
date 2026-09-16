"""Independent, account-owned vocabulary journey with optimistic concurrency."""
from alembic import op
import sqlalchemy as sa
revision = 'i5a0b8d4e6f2'
down_revision = 'h4f9a7c3d5e1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('a2_vocabulary_journey',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False),
        sa.Column('last_request', sa.String(), nullable=True))


def downgrade():
    op.drop_table('a2_vocabulary_journey')
