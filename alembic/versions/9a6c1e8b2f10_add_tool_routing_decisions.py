"""Add tool routing decisions table

Revision ID: 9a6c1e8b2f10
Revises: 4b2f5a2f3d2a
Create Date: 2026-04-02 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9a6c1e8b2f10"
down_revision: Union[str, Sequence[str], None] = "4b2f5a2f3d2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tool_routing_decisions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tool_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(), nullable=True),
        sa.Column("backend_selected", sa.String(), nullable=False),
        sa.Column("backend_candidates", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("('[]'::jsonb)"), nullable=True),
        sa.Column("task_description", sa.String(), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("performance_score", sa.Float(), nullable=False),
        sa.Column("composite_score", sa.Float(), nullable=False),
        sa.Column("token_cost_est", sa.Float(), nullable=False),
        sa.Column("token_cost_actual", sa.Float(), nullable=False),
        sa.Column("context_overhead_est", sa.Float(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tool_id"], ["tool_registry.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tool_routing_decisions_backend_selected"), "tool_routing_decisions", ["backend_selected"], unique=False)
    op.create_index(op.f("ix_tool_routing_decisions_created_at"), "tool_routing_decisions", ["created_at"], unique=False)
    op.create_index(op.f("ix_tool_routing_decisions_tool_id"), "tool_routing_decisions", ["tool_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tool_routing_decisions_tool_id"), table_name="tool_routing_decisions")
    op.drop_index(op.f("ix_tool_routing_decisions_created_at"), table_name="tool_routing_decisions")
    op.drop_index(op.f("ix_tool_routing_decisions_backend_selected"), table_name="tool_routing_decisions")
    op.drop_table("tool_routing_decisions")
