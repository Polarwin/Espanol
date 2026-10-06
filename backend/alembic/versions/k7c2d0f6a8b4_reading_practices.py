"""Private generated reading exercises, separate from scored assessments."""
from alembic import op
import sqlalchemy as sa

revision = 'k7c2d0f6a8b4'
down_revision = 'j6b1c9e5f7a3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('reading_practices',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('stage', sa.String(), nullable=False),
        sa.Column('level', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('source_key', sa.String(), nullable=False),
        sa.Column('source_title', sa.String(), nullable=False),
        sa.Column('pack', sa.JSON(), nullable=True),
        sa.Column('answers', sa.JSON(), nullable=False),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_index('ix_reading_practices_user_id', 'reading_practices', ['user_id'])


def downgrade():
    op.drop_table('reading_practices')
