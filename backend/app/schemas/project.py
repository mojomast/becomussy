"""
becomussy – Project & Commitment Pydantic schemas.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import StatusEnum


# ── Project CRUD ───────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    model_config = ConfigDict(extra="forbid")

    name: str
    purpose: str | None = None
    origin: str | None = None
    current_phase: str | None = None
    milestones_json: list[dict[str, Any]] | None = None
    artifacts_json: list[dict[str, Any]] | None = None
    linked_themes: list[str] | None = None
    linked_people: list[str] | None = None
    next_steps_json: list[dict[str, Any]] | None = None
    review_cadence: str | None = None
    status: StatusEnum | None = None


class ProjectUpdate(BaseModel):
    """Schema for partially updating a project (PATCH)."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    purpose: str | None = None
    origin: str | None = None
    current_phase: str | None = None
    milestones_json: list[dict[str, Any]] | None = None
    artifacts_json: list[dict[str, Any]] | None = None
    linked_themes: list[str] | None = None
    linked_people: list[str] | None = None
    next_steps_json: list[dict[str, Any]] | None = None
    review_cadence: str | None = None
    status: StatusEnum | None = None


class CommitmentRead(BaseModel):
    """Full read model for a commitment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID | None
    commitment_text: str
    made_to: str | None
    date_made: date | None
    due_date: date | None
    status: str
    evidence_of_fulfillment: str | None
    risk_if_missed: str | None
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None


class ProjectRead(BaseModel):
    """Full read model for a project."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    purpose: str | None
    origin: str | None
    current_phase: str | None
    milestones_json: Any
    artifacts_json: Any
    linked_themes: list[str] | None
    linked_people: list[str] | None
    next_steps_json: Any
    review_cadence: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None
    commitments: list[CommitmentRead] = Field(default_factory=list)


# ── Commitment CRUD ────────────────────────────────────────────────────


class CommitmentCreate(BaseModel):
    """Schema for creating a new commitment."""

    model_config = ConfigDict(extra="forbid")

    project_id: uuid.UUID | None = None
    commitment_text: str
    made_to: str | None = None
    date_made: date | None = None
    due_date: date | None = None
    status: StatusEnum | None = None
    risk_if_missed: str | None = None


class CommitmentUpdate(BaseModel):
    """Schema for partially updating a commitment (PATCH)."""

    model_config = ConfigDict(extra="forbid")

    project_id: uuid.UUID | None = None
    commitment_text: str | None = None
    made_to: str | None = None
    date_made: date | None = None
    due_date: date | None = None
    status: StatusEnum | None = None
    evidence_of_fulfillment: str | None = None
    risk_if_missed: str | None = None


# ── Search parameters ──────────────────────────────────────────────────


class CommitmentSearchParams(BaseModel):
    """Query parameters for listing/filtering commitments."""

    model_config = ConfigDict(extra="forbid")

    project_id: uuid.UUID | None = None
    status: StatusEnum | None = None
    overdue: bool | None = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)
