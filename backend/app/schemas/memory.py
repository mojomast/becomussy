"""
becomussy – Memory Pydantic schemas.

Covers MemoryItem CRUD, search, links, and special operations.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import (
    ApprovalStateEnum,
    ConfidenceLevelEnum,
    MemoryTypeEnum,
    ProvenanceSchema,
    StatusEnum,
)


# ── MemoryItem CRUD ────────────────────────────────────────────────────


class MemoryItemCreate(BaseModel):
    """Schema for creating a new memory item."""

    model_config = ConfigDict(extra="forbid")

    memory_type: MemoryTypeEnum
    timestamp: datetime | None = None
    summary: str | None = None
    statement: str | None = None
    importance_score: Decimal | None = Field(None, ge=0, le=999.99)
    confidence_level: ConfidenceLevelEnum | None = None
    metadata: dict[str, Any] | None = None
    provenance: ProvenanceSchema | None = None
    source_kind: str | None = None
    source_ref: str | None = None


class MemoryItemUpdate(BaseModel):
    """Schema for partially updating a memory item (PATCH)."""

    model_config = ConfigDict(extra="forbid")

    memory_type: MemoryTypeEnum | None = None
    timestamp: datetime | None = None
    summary: str | None = None
    statement: str | None = None
    importance_score: Decimal | None = Field(None, ge=0, le=999.99)
    salience_score: Decimal | None = Field(None, ge=0, le=999.99)
    confidence_level: ConfidenceLevelEnum | None = None
    status: StatusEnum | None = None
    approval_state: ApprovalStateEnum | None = None
    metadata: dict[str, Any] | None = None
    source_kind: str | None = None
    source_ref: str | None = None


class MemoryLinkRead(BaseModel):
    """Read schema for a memory link."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    from_memory_id: uuid.UUID
    to_memory_id: uuid.UUID
    link_type: str
    weight: Decimal | None
    created_at: datetime


class MemoryItemRead(BaseModel):
    """Full read model for a memory item."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    memory_type: str
    timestamp: datetime
    summary: str | None
    statement: str | None
    importance_score: Decimal | None
    salience_score: Decimal | None
    confidence_level: str | None
    status: str
    approval_state: str
    source_kind: str | None
    source_ref: str | None
    provenance_json: dict[str, Any]
    metadata_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None
    outgoing_links: list[MemoryLinkRead] = Field(default_factory=list)
    incoming_links: list[MemoryLinkRead] = Field(default_factory=list)


# ── Search parameters ──────────────────────────────────────────────────


class MemorySearchParams(BaseModel):
    """Query parameters for searching memory items."""

    model_config = ConfigDict(extra="forbid")

    q: str | None = None
    memory_type: MemoryTypeEnum | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    project_id: uuid.UUID | None = None
    person: str | None = None
    identity_theme: str | None = None
    confidence: ConfidenceLevelEnum | None = None
    approval_state: ApprovalStateEnum | None = None
    status: StatusEnum | None = Field(None)
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


# ── Memory links ───────────────────────────────────────────────────────


class MemoryLinkCreate(BaseModel):
    """Schema for creating a link between two memory items."""

    model_config = ConfigDict(extra="forbid")

    from_memory_id: uuid.UUID
    to_memory_id: uuid.UUID
    link_type: str
    weight: Decimal | None = Field(None, ge=0, le=999.99)


# ── Special operations ─────────────────────────────────────────────────


class MemoryReinforceRequest(BaseModel):
    """Schema for reinforcing a memory (bump salience)."""

    model_config = ConfigDict(extra="forbid")

    reason: str
    source_ref: str | None = None


class MemoryContradictRequest(BaseModel):
    """Schema for marking a contradiction between memories."""

    model_config = ConfigDict(extra="forbid")

    contradicting_memory_id: uuid.UUID
    reason: str
