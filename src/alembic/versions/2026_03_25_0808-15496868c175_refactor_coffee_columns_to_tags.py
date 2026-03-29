"""refactor coffee columns to tags

Revision ID: 15496868c175
Revises: b673e336c240
Create Date: 2026-03-25 08:08:35.969544

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy.sql as sql


# revision identifiers, used by Alembic.
revision: str = "15496868c175"
down_revision: Union[str, Sequence[str], None] = "b673e336c240"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    roasted_coffees_table = sql.table(
        "roasted_coffees",
        sa.Column("id", sa.Integer),
        sa.Column("is_blend", sa.Boolean),
        sa.Column("profile", sa.JSON),
        sa.Column("notes", sa.JSON),
    )

    green_coffees_table = sql.table(
        "green_coffees",
        sa.Column("id", sa.Integer),
        sa.Column("process", sa.String),
        sa.Column("varieties", sa.JSON),
        sa.Column("details", sa.JSON),
    )

    # Create and populate coffee_tag_types table
    tag_type_table = op.create_table(
        "coffee_tag_types",
        sa.Column("name", sa.String, primary_key=True),
        sa.Column("description", sa.String),
    )
    op.bulk_insert(
        tag_type_table,
        [
            {"name": "process", "description": "[str]"},
            {"name": "variety", "description": "[str]"},
            {
                "name": "profile",
                "description": "[str] The vendor's intended attributes and uses, as well as information about single-origin/blend/decaf.",
            },
            {"name": "tasting", "description": "[str] Vendor-provided tasting notes."},
        ],
    )

    # Create `roasted_coffee_tags` table
    roasted_coffee_tags_table = op.create_table(
        "roasted_coffee_tags",
        sa.Column(
            "roasted_id",
            sa.Integer,
            sa.ForeignKey("roasted_coffees.id"),
            primary_key=True,
        ),
        sa.Column(
            "type",
            sa.String,
            sa.ForeignKey(
                "coffee_tag_types.name", ondelete="RESTRICT", onupdate="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column("value", sa.String, primary_key=True),
        comment="Vendor-provided details.",
    )

    # Convert roasted coffee `is_blend` column to tags (as profile)
    connection.execute(
        sa.insert(roasted_coffee_tags_table).from_select(
            ["roasted_id", "type", "value"],
            sa.select(
                roasted_coffees_table.c.id,
                sa.literal("profile"),
                sa.case(
                    (roasted_coffees_table.c.is_blend == False, "single origin"),
                    else_="blend",
                ),
            ),
        )
    )

    op.drop_column("roasted_coffees", "is_blend")

    # Convert roasted coffee `profile` column to tags
    connection.execute(
        sa.insert(roasted_coffee_tags_table).from_select(
            ["roasted_id", "type", "value"],
            sa.select(
                roasted_coffees_table.c.id,
                sa.literal("profile"),
                sa.func.json_array_elements_text(roasted_coffees_table.c.profile),
            ),
        )
    )

    op.drop_column("roasted_coffees", "profile")

    # Convert roasted coffee `notes` column to tags
    connection.execute(
        sa.insert(roasted_coffee_tags_table).from_select(
            ["roasted_id", "type", "value"],
            sa.select(
                roasted_coffees_table.c.id,
                sa.literal("tasting"),
                sa.func.json_array_elements_text(roasted_coffees_table.c.notes),
            ),
        )
    )

    op.drop_column("roasted_coffees", "notes")

    # Create `green_coffee_tags` table
    green_coffee_tags_table = op.create_table(
        "green_coffee_tags",
        sa.Column(
            "green_id",
            sa.Integer,
            sa.ForeignKey("green_coffees.id"),
            primary_key=True,
        ),
        sa.Column(
            "type",
            sa.String,
            sa.ForeignKey(
                "coffee_tag_types.name", ondelete="RESTRICT", onupdate="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column("value", sa.String, primary_key=True),
        comment="Vendor-provided details.",
    )

    # Convert green coffee `varieties` column to tags
    connection.execute(
        sa.insert(green_coffee_tags_table).from_select(
            ["green_id", "type", "value"],
            sa.select(
                green_coffees_table.c.id,
                sa.literal("variety"),
                sa.func.json_array_elements_text(green_coffees_table.c.varieties),
            ),
        )
    )

    op.drop_column("green_coffees", "varieties")

    # Convert green coffee `process` column to tags, including information from `details`
    connection.execute(
        sa.insert(green_coffee_tags_table).from_select(
            ["green_id", "type", "value"],
            sa.select(
                green_coffees_table.c.id,
                sa.literal("process"),
                green_coffees_table.c.process,
            ),
        )
    )

    op.drop_column("green_coffees", "process")

    connection.execute(
        sa.insert(green_coffee_tags_table).from_select(
            ["green_id", "type", "value"],
            sa.select(
                green_coffees_table.c.id,
                sa.literal("process"),
                sa.func.json_array_elements_text(
                    green_coffees_table.c.details["process"]
                ),
            ),
        )
    )

    # Remove `process` field from green coffee `details` (JSON) column
    rows = connection.execute(
        sa.select(green_coffees_table.c.id, green_coffees_table.c.details)
    ).all()

    for row in rows:
        connection.execute(
            green_coffees_table.update()
            .values(
                {"details": {k: v for k, v in row.details.items() if k != "process"}}
            )
            .where(green_coffees_table.c.id == row.id)
        )


def downgrade() -> None:
    connection = op.get_bind()

    roasted_coffees_table = sql.table(
        "roasted_coffees",
        sa.Column("id", sa.Integer),
        sa.Column("is_blend", sa.Boolean),
        sa.Column("profile", sa.JSON),
        sa.Column("notes", sa.JSON),
    )

    roasted_coffee_tags_table = sql.table(
        "roasted_coffee_tags",
        sa.Column("roasted_id", sa.Integer),
        sa.Column("type", sa.String),
        sa.Column("value", sa.String),
    )

    green_coffees_table = sql.table(
        "green_coffees",
        sa.Column("id", sa.Integer),
        sa.Column("varieties", sa.JSON),
        sa.Column("process", sa.String),
        sa.Column("details", sa.JSON),
    )

    green_coffee_tags_table = sql.table(
        "green_coffee_tags",
        sa.Column("green_id", sa.Integer),
        sa.Column("type", sa.String),
        sa.Column("value", sa.String),
    )

    # Create and populate roasted coffee `is_blend` column from profiles
    op.add_column("roasted_coffees", sa.Column("is_blend", sa.Boolean))

    connection.execute(
        sa.update(roasted_coffees_table).values(
            {
                "is_blend": (
                    ~sa.select(roasted_coffee_tags_table)
                    .where(
                        roasted_coffee_tags_table.c.roasted_id
                        == roasted_coffees_table.c.id,
                        roasted_coffee_tags_table.c.value == "single origin",
                    )
                    .exists()
                )
            }
        )
    )

    op.alter_column(
        "roasted_coffees", "is_blend", existing_nullable=True, nullable=False
    )

    # Create and populate roasted coffee `profile` column
    op.add_column("roasted_coffees", sa.Column("profile", sa.JSON))

    profiles_list_cte = (
        sa.select(
            roasted_coffee_tags_table.c.roasted_id.label("roasted_id"),
            sa.func.json_agg(roasted_coffee_tags_table.c.value).label("profiles"),
        )
        .where(
            roasted_coffee_tags_table.c.type == "profile",
            ~roasted_coffee_tags_table.c.value.in_(["single origin", "blend"]),
        )
        .group_by(roasted_coffee_tags_table.c.roasted_id)
    ).cte()

    connection.execute(
        sa.update(roasted_coffees_table).values(
            {
                "profile": sa.func.coalesce(
                    sa.select(profiles_list_cte.c.profiles)
                    .where(profiles_list_cte.c.roasted_id == roasted_coffees_table.c.id)
                    .scalar_subquery(),
                    "[]",
                )
            }
        )
    )

    # Create and populate roasted coffee `notes` column
    op.add_column("roasted_coffees", sa.Column("notes", sa.JSON))

    notes_list_cte = (
        sa.select(
            roasted_coffee_tags_table.c.roasted_id.label("roasted_id"),
            sa.func.json_agg(roasted_coffee_tags_table.c.value).label("notes"),
        )
        .where(roasted_coffee_tags_table.c.type == "tasting")
        .group_by(roasted_coffee_tags_table.c.roasted_id)
    ).cte()

    connection.execute(
        sa.update(roasted_coffees_table).values(
            {
                "notes": sa.func.coalesce(
                    sa.select(notes_list_cte.c.notes)
                    .where(notes_list_cte.c.roasted_id == roasted_coffees_table.c.id)
                    .scalar_subquery(),
                    "[]",
                )
            }
        )
    )

    # Create and populate green coffee `process` column, adding extra process
    # descriptors to `detail` (JSON) column under the `processes` key

    op.add_column("green_coffees", sa.Column("process", sa.String))

    processes_data = [
        {
            "green_id": green_id,
            "process": processes[0],
            "processes_secondary": processes[1:],
            "details": details,
        }
        for green_id, processes, details in connection.execute(
            sa.select(
                green_coffee_tags_table.c.green_id,
                sa.func.array_agg(green_coffee_tags_table.c.value).label("processes"),
                sa.func.any_value(green_coffees_table.c.details),
            )
            .join(
                green_coffees_table,
                green_coffees_table.c.id == green_coffee_tags_table.c.green_id,
            )
            .where(
                green_coffee_tags_table.c.type == "process",
            )
            .group_by(green_coffee_tags_table.c.green_id)
        )
    ]

    for data in processes_data:
        green_id: int = data["green_id"]
        process: str = data["process"]
        processes_secondary: list | None = data.get("processes_secondary")
        details: dict = data.get("details", {})

        connection.execute(
            green_coffees_table.update()
            .where(green_coffees_table.c.id == green_id)
            .values(
                {
                    "process": process,
                    "details": (
                        {"process": processes_secondary, **details}
                        if processes_secondary
                        else details
                    ),
                }
            )
        )

    # Create and populate green coffee `varieties` column
    op.add_column("green_coffees", sa.Column("varieties", sa.JSON))

    connection.execute(
        green_coffees_table.update().values(
            {
                "varieties": sa.func.coalesce(
                    sa.select(sa.func.json_agg(green_coffee_tags_table.c.value))
                    .where(
                        green_coffee_tags_table.c.type == "variety",
                        green_coffee_tags_table.c.green_id == green_coffees_table.c.id,
                    )
                    .group_by(green_coffee_tags_table.c.green_id)
                    .scalar_subquery(),
                    "[]",
                )
            }
        )
    )

    # Drop `green_coffee_tags` table
    op.drop_table("green_coffee_tags")

    # Drop `roasted_coffee_tags` table
    op.drop_table("roasted_coffee_tags")

    # Drop coffee_tag_types table
    op.drop_table("coffee_tag_types")
