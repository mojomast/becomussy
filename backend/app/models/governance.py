"""
becomussy – ApprovalDecision ORM model.

Maps to the ``approval_decisions`` table.  Each row is an immutable record of
an approval, rejection, or deferral decision for a revision proposal.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApprovalDecision(Base):
    """Immutable record of an approval / rejection / deferral decision."""

    __tablename__ = "approval_decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    revision_proposal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("revision_proposals.id"),
        nullable=False,
    )
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    decided_by: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_evidence_json: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    immutable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )
