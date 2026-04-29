"""add address fields to user profile

Revision ID: 2746a4ac7d00
Revises: 
Create Date: 2026-04-29 17:03:16.939519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2746a4ac7d00'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_profiles', sa.Column('address_line_1', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('address_line_2', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('city', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('state', sa.String(), nullable=True))
    op.add_column('user_profiles', sa.Column('pincode', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
