"""add user fields for profile

Revision ID: fdb87e785df3
Revises: 1be2be374dcf
Create Date: 2026-04-02 00:25:02.179850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdb87e785df3'
down_revision: Union[str, Sequence[str], None] = '1be2be374dcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('school', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('streak_days', sa.Integer, server_default='0', nullable=False))
    op.add_column('users', sa.Column('last_activity_date', sa.Date, nullable=True))
def downgrade():
    op.drop_column('users', 'school')
    op.drop_column('users', 'city')
    op.drop_column('users', 'streak_days')
    op.drop_column('users', 'last_activity_date')