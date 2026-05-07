"""add bank_id to loan_application

Revision ID: ec15e839a931
Revises: 9cc7b974801d
Create Date: 2026-05-06 21:45:08.433826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec15e839a931'
down_revision: Union[str, Sequence[str], None] = '9cc7b974801d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('loan_applications', sa.Column('bank_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
    'fk_loan_bank',
    'loan_applications',
    'user_bank_details',
    ['bank_id'],
    ['id']
    )


