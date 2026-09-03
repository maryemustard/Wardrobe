"""create items table

Revision ID: 0001_create_items
Revises:
Create Date: 2026-09-03

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_items"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("color", sa.String(length=60), nullable=True),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("size", sa.String(length=40), nullable=True),
        sa.Column("season", sa.String(length=20), nullable=True),
        sa.Column("material", sa.String(length=120), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("image_public_id", sa.String(length=200), nullable=True),
        sa.Column("is_archived", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_items_category", "items", ["category"])
    op.create_index("ix_items_is_archived", "items", ["is_archived"])


def downgrade() -> None:
    op.drop_index("ix_items_is_archived", table_name="items")
    op.drop_index("ix_items_category", table_name="items")
    op.drop_table("items")
