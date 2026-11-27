"""create table identities

Revision ID: 30c532253f25
Revises: d519f4fd67ea
Create Date: 2026-11-23 05:41:39.940103

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy.sql as sql

# revision identifiers, used by Alembic.
revision: str = "30c532253f25"
down_revision: Union[str, Sequence[str], None] = "d519f4fd67ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    connection = op.get_bind()

    roasters_table = sql.table(
        "roasters",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String),
        sa.Column("normalized_name", sa.String),
        sa.Column("city", sa.String),
        sa.Column("country", sa.String),
        sa.Column("details", sa.JSON),
    )

    """Upgrade schema."""
    identities_table = op.create_table(
        "identities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("country_id", sa.String(length=2), nullable=False),
        sa.Column(
            "details",
            sa.JSON(),
            server_default="{}",
            nullable=True,
            comment="Can include contact information, website, socials profiles, location details, etc.",
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "normalized_name",
            sa.String(),
            nullable=False,
            comment="`name` column normalized to remove case, accents, punctuation",
        ),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="List of identities of coffee-related companies or people.",
    )

    op.create_table(
        "location_associations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("identity_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.String(),
            nullable=True,
            comment="type of location (e.g. roastery, coffeeshop, popup, restaurant)",
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("address_detail", sa.String(), nullable=True),
        sa.Column("neighborhood", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("country_id", sa.String(length=2), nullable=False),
        sa.Column("date_opened", sa.DateTime(), nullable=True),
        sa.Column("date_closed", sa.DateTime(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["country_id"],
            ["countries.id"],
            name=op.f("fk_location_associations_country_id_countries"),
        ),
        sa.ForeignKeyConstraint(
            ["identity_id"],
            ["identities.id"],
            name=op.f("fk_location_associations_identity_id_identities"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_location_associations")),
    )

    # Seed roaster identities
    connection.execute(
        sa.insert(identities_table).from_select(
            ["name", "normalized_name", "city", "country_id", "details"],
            sa.select(
                roasters_table.c.name,
                roasters_table.c.normalized_name,
                roasters_table.c.city,
                roasters_table.c.country,
                roasters_table.c.details,
            ),
        )
    )

    # Reidentify roasters and drop identity columns
    roaster_id_subq = (
        sa.select(identities_table.c.id)
        .where(identities_table.c.normalized_name == roasters_table.c.normalized_name)
        .scalar_subquery()
    )

    connection.execute(sa.update(roasters_table).values(id=roaster_id_subq))

    op.drop_column("roasters", "name")
    op.drop_column("roasters", "normalized_name")
    op.drop_column("roasters", "city")
    op.drop_column("roasters", "state")
    op.drop_column("roasters", "country")
    op.drop_column("roasters", "details")

    # Seed service identities
    service_table = sql.table(
        "service",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String),
        sa.Column("normalized_name", sa.String),
    )

    connection.execute(
        sa.insert(identities_table).from_select(
            ["name", "normalized_name", "country_id"],
            sa.select(
                service_table.c.name,
                service_table.c.normalized_name,
                sa.literal("US"),
            ).where(
                service_table.c.normalized_name.not_in(
                    sa.select(identities_table.c.normalized_name)
                )
            ),
        )
    )

    # Reidentify service and drop identity columns
    service_id_subq = (
        sa.select(identities_table.c.id)
        .where(identities_table.c.normalized_name == service_table.c.normalized_name)
        .scalar_subquery()
    )

    connection.execute(sa.update(service_table).values(id=service_table.c.id + 10000))
    connection.execute(sa.update(service_table).values(id=service_id_subq))

    op.drop_column("service", "name")
    op.drop_column("service", "normalized_name")


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()

    identities_table = sql.table(
        "identities",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String),
        sa.Column("normalized_name", sa.String),
        sa.Column("city", sa.String),
        sa.Column("country_id", sa.String),
        sa.Column("details", sa.JSON),
    )

    service_table = sql.table(
        "service",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String),
        sa.Column("normalized_name", sa.String),
    )

    roasters_table = sql.table(
        "roasters",
        sa.Column("id", sa.Integer),
        sa.Column("name", sa.String),
        sa.Column("normalized_name", sa.String),
        sa.Column("city", sa.String),
        sa.Column("country", sa.String),
        sa.Column("details", sa.JSON),
    )

    # Repopulate service table with identities
    op.add_column("service", sa.Column("name", sa.String))
    op.add_column("service", sa.Column("normalized_name", sa.String))

    connection.execute(
        sa.update(service_table)
        .where(service_table.c.id == identities_table.c.id)
        .values(
            **{
                "name": identities_table.c.name,
                "normalized_name": identities_table.c.normalized_name,
            }
        )
    )

    op.alter_column("service", "name", nullable=False)
    op.alter_column("service", "normalized_name", nullable=False)

    # Repopulate roasters table with identities
    op.add_column("roasters", sa.Column("name", sa.String))
    op.add_column("roasters", sa.Column("normalized_name", sa.String))
    op.add_column("roasters", sa.Column("city", sa.String))
    op.add_column("roasters", sa.Column("state", sa.String))
    op.add_column("roasters", sa.Column("country", sa.String))
    op.add_column("roasters", sa.Column("details", sa.JSON))

    connection.execute(
        sa.update(roasters_table)
        .where(roasters_table.c.id == identities_table.c.id)
        .values(
            **{
                "name": identities_table.c.name,
                "normalized_name": identities_table.c.normalized_name,
                "city": identities_table.c.city,
                "country": identities_table.c.country_id,
                "details": identities_table.c.details,
            }
        )
    )

    op.drop_table("identities")
