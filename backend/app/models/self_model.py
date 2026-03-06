"""
becomussy – SelfModelVersion ORM model.

Maps to the ``self_model_versions`` table. Each row is a complete snapshot of
the agent's self-model at a point in time, enabling versioned comparison
and structured diffing.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SelfModelVersion(Base):
    """A versioned snapshot of the agent's self-model."""

    __tablename__ = "self_model_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    authoring_process: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_state: Mapped[str] = mapped_column(Text, nullable=False)
    diff_from_prior_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )
    evidence_links_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    descriptive_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    aspirational_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    constrained_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    relational_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[str] = mapped_column(Text, nullable=False)
