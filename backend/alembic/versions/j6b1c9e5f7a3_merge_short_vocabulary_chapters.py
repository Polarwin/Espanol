"""Merge short glossary tails; preserve in-flight questions and review queues."""
from copy import deepcopy

from alembic import op
import sqlalchemy as sa

revision = 'j6b1c9e5f7a3'
down_revision = 'i5a0b8d4e6f2'
branch_labels = None
depends_on = None

# Frozen original layout: independent of future edits to curriculum code.
OLD = []
for group, count in [(5, 19), (3, 10), (2, 22), (1, 6), (4, 4),
                     (0, 4), (6, 15), (9, 7), (7, 38), (8, 10)]:
    for start in range(0, count, 5):
        OLD.append([f'{group}-{i}' for i in range(start, min(start + 5, count))])
GROUPED = []
for index in range(len(OLD)):
    if index in {10, 12, 19}:
        GROUPED[-1].append(index)
    else:
        GROUPED.append([index])


def remap(data):
    result = deepcopy(data)
    old_index = data['chapter']
    if old_index >= len(OLD):
        result['chapter'] = len(GROUPED)
        return result
    new_index, members = next((i, members) for i, members in enumerate(GROUPED) if old_index in members)
    result['chapter'] = new_index
    if len(members) > 1:
        if old_index != members[0]:
            # The preceding part was already completed. Keep only the unfinished tail.
            result['chapter_words'] = OLD[old_index]
        elif data['phase'] in {'quiz', 'summary'}:
            # Do not insert unseen words into an existing quiz or discard its score.
            result['chapter_words'] = OLD[old_index]
            result['continuation_words'] = [word for member in members[1:] for word in OLD[member]]
        # Mid-teaching in the first part: existing index stays valid in the merged list.
    return result


def upgrade():
    table = sa.table('a2_vocabulary_journey', sa.column('user_id', sa.Integer),
                     sa.column('data', sa.JSON), sa.column('revision', sa.Integer),
                     sa.column('last_request', sa.String))
    connection = op.get_bind()
    for row in connection.execute(sa.select(table)).mappings().all():
        connection.execute(table.update().where(table.c.user_id == row['user_id']).values(
            data=remap(row['data']), revision=row['revision'] + 1, last_request=None))


def downgrade():
    raise RuntimeError('Restoring the old layout requires an explicit progress migration; do not reset learner progress.')
