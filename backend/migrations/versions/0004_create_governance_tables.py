"""create approval_decisions table

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "approval_decisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "revision_proposal_id",
            UUID(as_uuid=True),
            sa.ForeignKey("revision_proposals.id"),
            nullable=False,
        ),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("decided_by", sa.Text(), nullable=False),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "requested_evidence_json",
            JSONB,
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "immutable",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )

    # Index on revision_proposal_id for fast lookups by proposal
    op.create_index(
        "ix_approval_decisions_revision_proposal_id",
        "approval_decisions",
        ["revision_proposal_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_approval_decisions_revision_proposal_id",
        table_name="approval_decisions",
    )
    op.drop_table("approval_decisions")
