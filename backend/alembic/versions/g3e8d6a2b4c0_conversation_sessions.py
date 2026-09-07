"""Durable, user-owned conversation history and duplicate-turn protection."""
from alembic import op
import sqlalchemy as sa
revision = 'g3e8d6a2b4c0'
down_revision = 'b4e8c2a71d05'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('conversation_sessions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('lesson_id', sa.Integer(), sa.ForeignKey('lessons.id'), nullable=False),
        sa.Column('turn', sa.Integer(), nullable=False),
        sa.Column('history', sa.JSON(), nullable=False),
        sa.Column('last_request', sa.String(), nullable=True),
        sa.Column('last_result', sa.JSON(), nullable=True))
    op.create_index('ix_conversation_sessions_user_id', 'conversation_sessions', ['user_id'])


def downgrade():
    op.drop_table('conversation_sessions')
