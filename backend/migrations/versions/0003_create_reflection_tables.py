"""create reflection tables (journal, self-model, revision proposals)

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── journal_entries ─────────────────────────────────────────────────
    op.create_table(
        "journal_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("entry_type", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body_md", sa.Text(), nullable=False),
        sa.Column("confidence_level", sa.Text(), nullable=True),
        sa.Column(
            "tags",
            ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "linked_memory_ids",
            ARRAY(UUID(as_uuid=True)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "linked_project_ids",
            ARRAY(UUID(as_uuid=True)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "linked_identity_themes",
            ARRAY(sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "follow_up_candidates",
            JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "provenance_json",
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
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("updated_by", sa.Text(), nullable=False),
    )

    # ── self_model_versions ─────────────────────────────────────────────
    op.create_table(
        "self_model_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("authoring_process", sa.Text(), nullable=False),
        sa.Column("confidence_level", sa.Text(), nullable=True),
        sa.Column("approval_state", sa.Text(), nullable=False),
        sa.Column(
            "diff_from_prior_json",
            JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "evidence_links_json",
            JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column("descriptive_json", JSONB, nullable=False),
        sa.Column("aspirational_json", JSONB, nullable=False),
        sa.Column("constrained_json", JSONB, nullable=False),
        sa.Column("relational_json", JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("created_by", sa.Text(), nullable=False),
    )

    # ── revision_proposals ──────────────────────────────────────────────
    op.create_table(
        "revision_proposals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("revision_type", sa.Text(), nullable=False),
        sa.Column("target_entity_type", sa.Text(), nullable=False),
        sa.Column(
            "target_entity_id", UUID(as_uuid=True), nullable=True
        ),
        sa.Column("stage", sa.Text(), nullable=False),
        sa.Column("risk_class", sa.Text(), nullable=False),
        sa.Column("policy_result", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column(
            "evidence_json",
            JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "simulation_json",
            JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "proposed_diff_json",
            JSONB,
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "approval_state",
            sa.Text(),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "monitoring_plan_json",
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
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("updated_by", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("revision_proposals")
    op.drop_table("self_model_versions")
    op.drop_table("journal_entries")
