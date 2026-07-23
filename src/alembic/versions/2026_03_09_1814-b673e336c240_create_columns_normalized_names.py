"""create columns: normalized names

Revision ID: b673e336c240
Revises: e3ff81cf0bba
Create Date: 2026-03-09 18:14:07.058347

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from src.db.utilities import normalized_text


# revision identifiers, used by Alembic.
revision: str = "b673e336c240"
down_revision: Union[str, Sequence[str], None] = "e3ff81cf0bba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_normalized_column(
    table_name: str,
    column_name: str,
    normalized_column_name: str = "",
    nullable: bool = True,
):
    """
    Create and fill a accent, case, and punctuation-insensitive TEXT column
    using data from an existing column.
    """

    if not normalized_column_name:
        normalized_column_name = f"normalized_{column_name}"

    bind = op.get_bind()
    table_obj = table(
        table_name,
        column(column_name, sa.String),
        column(normalized_column_name, sa.String),
    )

    # Create column
    op.add_column(
        table_name,
        sa.Column(
            normalized_column_name,
            sa.String,
            comment=f"`{column_name}` column normalized to remove case, accents, punctuation",
            default=lambda context: normalized_text(
                context.get_current_parameters()[column_name]
            ),
            onupdate=lambda context: normalized_text(
                context.get_current_parameters()[column_name]
            ),
        ),
    )

    # Fill column
    values = bind.scalars(sa.select(table_obj.c[column_name])).all()

    for value in values:
        bind.execute(
            sa.update(table_obj)
            .where(table_obj.c[column_name] == value)
            .values({normalized_column_name: normalized_text(value)})
        )

    # Add constraints
    if nullable:
        op.alter_column(table_name, normalized_column_name, nullable=True)
    else:
        op.alter_column(table_name, normalized_column_name, nullable=False)


def upgrade() -> None:
    """Upgrade schema."""
    create_normalized_column("origins", "name", "normalized_name", nullable=False)
    create_normalized_column("green_coffees", "name", "normalized_name", nullable=False)
    create_normalized_column("roasted_coffees", "name", "normalized_name", nullable=False)
    create_normalized_column("roasters", "name", "normalized_name", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("origins", "normalized_name")
    op.drop_column("green_coffees", "normalized_name")
    op.drop_column("roasted_coffees", "normalized_name")
    op.drop_column("roasters", "normalized_name")
