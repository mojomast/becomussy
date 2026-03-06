"""
becomussy – Memory ORM models.

Maps to the ``memory_items`` and ``memory_links`` tables.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MemoryItem(Base):
    """A single memory entry in the becoming system."""

    __tablename__ = "memory_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    memory_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="episodic | semantic | autobiographical | working | relational",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="When the memory event occurred",
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    importance_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    salience_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        server_default="0.00",
    )
    confidence_level: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="low | medium | high",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="active",
    )
    approval_state: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="not_required",
    )
    source_kind: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    outgoing_links: Mapped[list[MemoryLink]] = relationship(
        "MemoryLink",
        foreign_keys="MemoryLink.from_memory_id",
        back_populates="from_memory",
        lazy="selectin",
    )
    incoming_links: Mapped[list[MemoryLink]] = relationship(
        "MemoryLink",
        foreign_keys="MemoryLink.to_memory_id",
        back_populates="to_memory",
        lazy="selectin",
    )


class MemoryLink(Base):
    """A directional link between two memory items."""

    __tablename__ = "memory_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    from_memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("memory_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("memory_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    link_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="supports | contradicts | elaborates | related",
    )
    weight: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        server_default="1.00",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    from_memory: Mapped[MemoryItem] = relationship(
        "MemoryItem",
        foreign_keys=[from_memory_id],
        back_populates="outgoing_links",
    )
    to_memory: Mapped[MemoryItem] = relationship(
        "MemoryItem",
        foreign_keys=[to_memory_id],
        back_populates="incoming_links",
    )
