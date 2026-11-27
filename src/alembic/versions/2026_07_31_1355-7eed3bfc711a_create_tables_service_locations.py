"""create tables service locations

Revision ID: 7eed3bfc711a
Revises: 15496868c175
Create Date: 2026-07-31 13:55:36.826193

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7eed3bfc711a"
down_revision: Union[str, Sequence[str], None] = "15496868c175"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "service",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "normalized_name",
            sa.String(),
            nullable=False,
            comment="`name` column normalized to remove case, accents, punctuation",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("service")
