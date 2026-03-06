"""
becomussy – Journal Pydantic schemas.

Request/response models for journal entry CRUD, search, and summarization.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Create ──────────────────────────────────────────────────────────────


class JournalEntryCreate(BaseModel):
    """Payload for creating a new journal entry."""

    model_config = ConfigDict(extra="forbid")

    entry_type: str
    title: str
    body_md: str
    confidence_level: str | None = None
    tags: list[str] = Field(default_factory=list)
    linked_memory_ids: list[uuid.UUID] = Field(default_factory=list)
    linked_project_ids: list[uuid.UUID] = Field(default_factory=list)
    linked_identity_themes: list[str] = Field(default_factory=list)
    follow_up_candidates: list[Any] = Field(default_factory=list)
    provenance: dict[str, Any] | None = None


# ── Update (PATCH) ──────────────────────────────────────────────────────


class JournalEntryUpdate(BaseModel):
    """Payload for updating a journal entry. All fields optional."""

    model_config = ConfigDict(extra="forbid")

    entry_type: str | None = None
    title: str | None = None
    body_md: str | None = None
    confidence_level: str | None = None
    tags: list[str] | None = None
    linked_memory_ids: list[uuid.UUID] | None = None
    linked_project_ids: list[uuid.UUID] | None = None
    linked_identity_themes: list[str] | None = None
    follow_up_candidates: list[Any] | None = None
    provenance: dict[str, Any] | None = None


# ── Read ────────────────────────────────────────────────────────────────


class JournalEntryRead(BaseModel):
    """Full journal entry returned from reads."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    timestamp: datetime
    entry_type: str
    title: str
    body_md: str
    confidence_level: str | None = None
    tags: list[str]
    linked_memory_ids: list[uuid.UUID]
    linked_project_ids: list[uuid.UUID]
    linked_identity_themes: list[str]
    follow_up_candidates: list[Any]
    provenance_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


# ── Search params ───────────────────────────────────────────────────────


class JournalSearchParams(BaseModel):
    """Query parameters for searching journal entries."""

    model_config = ConfigDict(extra="forbid")

    keyword: str | None = None
    entry_type: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    linked_project_id: uuid.UUID | None = None
    linked_theme: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


# ── Summarize request ──────────────────────────────────────────────────


class JournalSummarizeRequest(BaseModel):
    """Request body for journal summarization."""

    model_config = ConfigDict(extra="forbid")

    range_start: datetime
    range_end: datetime
    summary_type: str = "weekly"
