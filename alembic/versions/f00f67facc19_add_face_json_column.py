"""add face json column

Revision ID: f00f67facc19
Revises: 205a71686b1c
Create Date: 2024-11-02 22:41:21.628187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f00f67facc19'
down_revision: Union[str, None] = '205a71686b1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('faces') as batch_op:
        batch_op.add_column(sa.Column('face_data', sa.String(), nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('faces') as batch_op:
        batch_op.drop_column('face_data')
