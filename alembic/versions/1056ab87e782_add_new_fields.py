"""Add new fields

Revision ID: 1056ab87e782
Revises:
Create Date: 2024-10-28 02:06:37.113656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1056ab87e782'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('images') as batch_op:
        batch_op.add_column(sa.Column('last_detection_run_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_images_last_detection_run_id', 'face_detection_runs', ['last_detection_run_id'], ['id'])

def downgrade() -> None:
    with op.batch_alter_table('images') as batch_op:
        batch_op.drop_constraint('fk_images_last_detection_run_id', 'images', type_='foreignkey')
        batch_op.drop_column('last_detection_run_id')
