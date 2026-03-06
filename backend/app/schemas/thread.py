"""
becomussy – Thread Pydantic schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import StatusEnum


# ── Thread CRUD ────────────────────────────────────────────────────────


class ThreadCreate(BaseModel):
    """Schema for creating a new thread."""

    model_config = ConfigDict(extra="forbid")

    title: str
    description: str | None = None
    thread_type: str | None = None
    status: StatusEnum | None = None
    urgency: int | None = Field(None, ge=1, le=10)
    importance: int | None = Field(None, ge=1, le=10)
    next_action: str | None = None
    blocker: str | None = None
    steward_visibility: str | None = None
    metadata_json: dict[str, Any] | None = None


class ThreadUpdate(BaseModel):
    """Schema for partially updating a thread (PATCH)."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    thread_type: str | None = None
    status: StatusEnum | None = None
    urgency: int | None = Field(None, ge=1, le=10)
    importance: int | None = Field(None, ge=1, le=10)
    next_action: str | None = None
    blocker: str | None = None
    steward_visibility: str | None = None
    metadata_json: dict[str, Any] | None = None


class ThreadRead(BaseModel):
    """Full read model for a thread."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    thread_type: str | None
    status: str
    opened_at: datetime
    updated_at: datetime
    urgency: int | None
    importance: int | None
    next_action: str | None
    blocker: str | None
    steward_visibility: str | None
    metadata_json: dict[str, Any]
    created_at: datetime
    updated_by: str | None


# ── Search parameters ──────────────────────────────────────────────────


class ThreadSearchParams(BaseModel):
    """Query parameters for listing/filtering threads."""

    model_config = ConfigDict(extra="forbid")

    status: StatusEnum | None = None
    thread_type: str | None = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)
