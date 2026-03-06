"""
becomussy – Thread ORM model.

Maps to the ``threads`` table.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Thread(Base):
    """An active thread of thought, concern, or ongoing topic."""

    __tablename__ = "threads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thread_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="e.g. identity, relational, project, emotional, practical",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="active",
    )
    opened_at: Mapped[datetime] = mapped_column(
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
    urgency: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="1-10 scale",
    )
    importance: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="1-10 scale",
    )
    next_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    blocker: Mapped[str | None] = mapped_column(Text, nullable=True)
    steward_visibility: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="private_runtime | steward_visible | shared | restricted",
    )
    metadata_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_by: Mapped[str | None] = mapped_column(Text, nullable=True)
