"""create core domain tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-06

Creates tables: memory_items, memory_links, threads, projects, commitments.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── memory_items ────────────────────────────────────────────────────
    op.create_table(
        "memory_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "memory_type",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("statement", sa.Text(), nullable=True),
        sa.Column("importance_score", sa.Numeric(5, 2), nullable=True),
        sa.Column(
            "salience_score",
            sa.Numeric(5, 2),
            nullable=True,
            server_default="0.00",
        ),
        sa.Column("confidence_level", sa.String(20), nullable=True),
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "approval_state",
            sa.String(30),
            nullable=False,
            server_default="not_required",
        ),
        sa.Column("source_kind", sa.String(50), nullable=True),
        sa.Column("source_ref", sa.Text(), nullable=True),
        sa.Column(
            "provenance_json",
            JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "metadata_json",
            JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Text(), nullable=True),
    )
    # Indexes for memory_items
    op.create_index("ix_memory_items_memory_type", "memory_items", ["memory_type"])
    op.create_index("ix_memory_items_status", "memory_items", ["status"])
    op.create_index("ix_memory_items_timestamp", "memory_items", ["timestamp"])
    op.create_index("ix_memory_items_confidence_level", "memory_items", ["confidence_level"])
    op.create_index("ix_memory_items_approval_state", "memory_items", ["approval_state"])

    # ── memory_links ────────────────────────────────────────────────────
    op.create_table(
        "memory_links",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "from_memory_id",
            UUID(as_uuid=True),
            sa.ForeignKey("memory_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "to_memory_id",
            UUID(as_uuid=True),
            sa.ForeignKey("memory_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("link_type", sa.String(50), nullable=False),
        sa.Column(
            "weight",
            sa.Numeric(5, 2),
            nullable=True,
            server_default="1.00",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_memory_links_from_memory_id", "memory_links", ["from_memory_id"])
    op.create_index("ix_memory_links_to_memory_id", "memory_links", ["to_memory_id"])
    op.create_index("ix_memory_links_link_type", "memory_links", ["link_type"])

    # ── threads ─────────────────────────────────────────────────────────
    op.create_table(
        "threads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("thread_type", sa.String(50), nullable=True),
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("urgency", sa.Integer(), nullable=True),
        sa.Column("importance", sa.Integer(), nullable=True),
        sa.Column("next_action", sa.Text(), nullable=True),
        sa.Column("blocker", sa.Text(), nullable=True),
        sa.Column("steward_visibility", sa.String(30), nullable=True),
        sa.Column(
            "metadata_json",
            JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_by", sa.Text(), nullable=True),
    )
    op.create_index("ix_threads_status", "threads", ["status"])
    op.create_index("ix_threads_thread_type", "threads", ["thread_type"])
    op.create_index("ix_threads_updated_at", "threads", ["updated_at"])

    # ── projects ────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("origin", sa.Text(), nullable=True),
        sa.Column("current_phase", sa.String(50), nullable=True),
        sa.Column(
            "milestones_json",
            JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "artifacts_json",
            JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column("linked_themes", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("linked_people", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column(
            "next_steps_json",
            JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column("review_cadence", sa.String(50), nullable=True),
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Text(), nullable=True),
    )
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_current_phase", "projects", ["current_phase"])

    # ── commitments ─────────────────────────────────────────────────────
    op.create_table(
        "commitments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("commitment_text", sa.Text(), nullable=False),
        sa.Column("made_to", sa.Text(), nullable=True),
        sa.Column("date_made", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.String(30),
            nullable=False,
            server_default="active",
        ),
        sa.Column("evidence_of_fulfillment", sa.Text(), nullable=True),
        sa.Column("risk_if_missed", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Text(), nullable=True),
    )
    op.create_index("ix_commitments_project_id", "commitments", ["project_id"])
    op.create_index("ix_commitments_status", "commitments", ["status"])
    op.create_index("ix_commitments_due_date", "commitments", ["due_date"])


def downgrade() -> None:
    op.drop_table("commitments")
    op.drop_table("projects")
    op.drop_table("threads")
    op.drop_table("memory_links")
    op.drop_table("memory_items")
