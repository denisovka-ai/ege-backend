"""add achievements tables

Revision ID: ca7931ceeb74
Revises: fb15124541bd
Create Date: 2026-04-02 00:41:27.627178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca7931ceeb74'
down_revision: Union[str, Sequence[str], None] = 'fb15124541bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table('achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('condition_type', sa.String(50), nullable=False),  # e.g., 'streak', 'perfect_test', etc.
        sa.Column('condition_value', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_achievements',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'achievement_id')
    )

def downgrade():
    op.drop_table('user_achievements')
    op.drop_table('achievements')
