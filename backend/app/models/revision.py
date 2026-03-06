"""
becomussy – RevisionProposal ORM model.

Maps to the ``revision_proposals`` table.  This model is referenced by the
governance service for approval workflows.  The table migration is owned
by the revisions subagent (migration 0003).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RevisionProposal(Base):
    """A proposed revision to the agent's self-model or other entity."""

    __tablename__ = "revision_proposals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    revision_type: Mapped[str] = mapped_column(Text, nullable=False)
    target_entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    target_entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    stage: Mapped[str] = mapped_column(
        Text, nullable=False, default="observation"
    )
    risk_class: Mapped[str] = mapped_column(
        Text, nullable=False, default="low"
    )
    policy_result: Mapped[str] = mapped_column(
        Text, nullable=False, default="approval_required"
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[list | dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    simulation_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )
    proposed_diff_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )
    approval_state: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="pending",
    )
    monitoring_plan_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[str] = mapped_column(Text, nullable=False)
    updated_by: Mapped[str] = mapped_column(Text, nullable=False)
