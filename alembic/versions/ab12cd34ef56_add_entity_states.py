"""Add entity states table

Revision ID: ab12cd34ef56
Revises: 9a6c1e8b2f10
Create Date: 2026-04-02 12:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ab12cd34ef56"
down_revision: Union[str, Sequence[str], None] = "9a6c1e8b2f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "entity_states",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("entity_key", sa.String(), nullable=False),
        sa.Column(
            "ontology_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("('{}'::jsonb)"),
            nullable=True,
        ),
        sa.Column("source_id", sa.String(), nullable=True),
        sa.Column("conflict_policy", sa.String(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entity_states_entity_key"), "entity_states", ["entity_key"], unique=False)
    op.create_index(op.f("ix_entity_states_source_id"), "entity_states", ["source_id"], unique=False)
    op.create_index(op.f("ix_entity_states_updated_at"), "entity_states", ["updated_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_entity_states_updated_at"), table_name="entity_states")
    op.drop_index(op.f("ix_entity_states_source_id"), table_name="entity_states")
    op.drop_index(op.f("ix_entity_states_entity_key"), table_name="entity_states")
    op.drop_table("entity_states")
