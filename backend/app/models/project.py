"""
becomussy – Project & Commitment ORM models.

Maps to the ``projects`` and ``commitments`` tables.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import ARRAY, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    """A project or initiative being tracked."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    origin: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Where this project originated from",
    )
    current_phase: Mapped[str | None] = mapped_column(String(50), nullable=True)
    milestones_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    artifacts_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    linked_themes: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
    linked_people: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
    )
    next_steps_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
    )
    review_cadence: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="e.g. weekly, biweekly, monthly",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="active",
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
    created_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    commitments: Mapped[list[Commitment]] = relationship(
        "Commitment",
        back_populates="project",
        lazy="selectin",
    )


class Commitment(Base):
    """A commitment made within a project context."""

    __tablename__ = "commitments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    commitment_text: Mapped[str] = mapped_column(Text, nullable=False)
    made_to: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Person or entity the commitment was made to",
    )
    date_made: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="active",
    )
    evidence_of_fulfillment: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_if_missed: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Description of risk if this commitment is not fulfilled",
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
    created_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    project: Mapped[Project | None] = relationship(
        "Project",
        back_populates="commitments",
    )
