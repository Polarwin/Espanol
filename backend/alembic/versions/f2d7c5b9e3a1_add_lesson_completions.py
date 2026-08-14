"""add durable lesson completions

Revision ID: f2d7c5b9e3a1
Revises: e1c6b4a8d2f0
"""
from alembic import op
import sqlalchemy as sa

revision = "f2d7c5b9e3a1"
down_revision = "e1c6b4a8d2f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lesson_completions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id"), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_lesson_completion"),
    )
    op.create_index("ix_lesson_completions_user_id", "lesson_completions", ["user_id"])
    op.create_index("ix_lesson_completions_lesson_id", "lesson_completions", ["lesson_id"])

    # Recover completed assessments from existing saved attempts.
    op.execute(sa.text("""
        INSERT INTO lesson_completions (user_id, lesson_id, completed_at)
        SELECT a.user_id, e.lesson_id, MAX(a.created_at)
        FROM attempts AS a
        JOIN exercises AS e ON e.id = a.exercise_id
        WHERE e.type IN ('vocabulary', 'grammar', 'writing', 'listening')
        GROUP BY a.user_id, e.lesson_id
        HAVING COUNT(DISTINCT a.exercise_id) = (
            SELECT COUNT(*) FROM exercises AS required
            WHERE required.lesson_id = e.lesson_id
              AND required.type IN ('vocabulary', 'grammar', 'writing', 'listening')
        )
    """))


def downgrade() -> None:
    op.drop_index("ix_lesson_completions_lesson_id", table_name="lesson_completions")
    op.drop_index("ix_lesson_completions_user_id", table_name="lesson_completions")
    op.drop_table("lesson_completions")
