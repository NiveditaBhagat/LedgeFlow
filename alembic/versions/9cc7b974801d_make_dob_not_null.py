"""make dob not null

Revision ID: 9cc7b974801d
Revises: 88dae4175082
Create Date: 2026-05-03 17:23:13.767692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cc7b974801d'
down_revision: Union[str, Sequence[str], None] = '88dae4175082'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        'user_profiles',
        'date_of_birth',
        existing_type=sa.Date(),
        nullable=False
    )


# def downgrade() -> None:
#     """Downgrade schema."""
#     pass
