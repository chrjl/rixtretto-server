"""create tables: origins, green_coffees

Revision ID: 762c128d99d2
Revises: ea84537a2edc
Create Date: 2025-12-26 14:37:21.068486

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "762c128d99d2"
down_revision: Union[str, Sequence[str], None] = "ea84537a2edc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "origins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "green_coffees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("process", sa.String(), nullable=True),
        sa.Column(
            "source",
            sa.String(),
            nullable=True,
            comment="The lowest level of traceability of the coffee, e.g. a farm name, cooperative, wet mill.",
        ),
        sa.Column(
            "source_type",
            sa.String(),
            nullable=True,
            comment="e.g. single estate, microlot, smallholder, cooperative, wet mill, purchasing station",
        ),
        sa.Column("community", sa.String(), nullable=True),
        sa.Column("region_id", sa.Integer(), nullable=True),
        sa.Column("varieties", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["region_id"],
            ["origins.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("green_coffees")
    op.drop_table("origins")
