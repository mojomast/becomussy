"""
becomussy – Self-Model Pydantic schemas.

Request/response models for self-model versioning, diffing, and history.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Section schema (structure for each self-model facet) ────────────────


class SelfModelSectionSchema(BaseModel):
    """Schema for one facet of the self-model (descriptive, aspirational, etc.)."""

    model_config = ConfigDict(extra="forbid")

    stable_traits: list[str] = Field(default_factory=list)
    current_aims: list[str] = Field(default_factory=list)
    recurring_strengths: list[str] = Field(default_factory=list)
    recurring_failure_modes: list[str] = Field(default_factory=list)
    attention_patterns: list[str] = Field(default_factory=list)
    memory_tendencies: list[str] = Field(default_factory=list)
    preferred_working_styles: list[str] = Field(default_factory=list)
    identity_narratives: list[str] = Field(default_factory=list)
    key_tensions: list[str] = Field(default_factory=list)
    value_hypotheses: list[str] = Field(default_factory=list)
    capability_boundaries: list[str] = Field(default_factory=list)
    open_development_questions: list[str] = Field(default_factory=list)


# ── Create ──────────────────────────────────────────────────────────────


class SelfModelVersionCreate(BaseModel):
    """Payload for creating a new self-model version."""

    model_config = ConfigDict(extra="forbid")

    authoring_process: str
    confidence_level: str | None = None
    descriptive_json: SelfModelSectionSchema
    aspirational_json: SelfModelSectionSchema
    constrained_json: SelfModelSectionSchema
    relational_json: SelfModelSectionSchema
    evidence_links: list[Any] = Field(default_factory=list)


# ── Read ────────────────────────────────────────────────────────────────


class SelfModelVersionRead(BaseModel):
    """Full self-model version returned from reads."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version_number: int
    timestamp: datetime
    authoring_process: str
    confidence_level: str | None = None
    approval_state: str
    diff_from_prior_json: dict[str, Any]
    evidence_links_json: list[Any] | dict[str, Any]
    descriptive_json: dict[str, Any]
    aspirational_json: dict[str, Any]
    constrained_json: dict[str, Any]
    relational_json: dict[str, Any]
    created_at: datetime
    created_by: str


# ── Diff request / response ─────────────────────────────────────────────


class SelfModelDiffRequest(BaseModel):
    """Request to compute a diff between two self-model versions."""

    model_config = ConfigDict(extra="forbid")

    from_version_id: uuid.UUID
    to_version_id: uuid.UUID


class DiffCategoryEnum(str, enum.Enum):
    """Categories for self-model diff items."""

    added_theme = "added_theme"
    removed_theme = "removed_theme"
    strengthened_tendency = "strengthened_tendency"
    weakened_tendency = "weakened_tendency"
    contradiction_detected = "contradiction_detected"
    evidence_added = "evidence_added"
    boundary_changed = "boundary_changed"
    aim_reprioritized = "aim_reprioritized"


class SelfModelDiffItem(BaseModel):
    """A single change between two self-model versions."""

    model_config = ConfigDict(extra="forbid")

    category: str
    section: str
    item: str
    prior_value: str | None = None
    new_value: str | None = None
    prior_confidence: str | None = None
    new_confidence: str | None = None
    evidence_links: list[Any] = Field(default_factory=list)


class SelfModelDiffResponse(BaseModel):
    """Structured diff between two self-model versions."""

    diffs: list[SelfModelDiffItem]
    from_version: int
    to_version: int


# ── History item ────────────────────────────────────────────────────────


class SelfModelHistoryItem(BaseModel):
    """Lightweight version header for history listings."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version_number: int
    timestamp: datetime
    authoring_process: str
    confidence_level: str | None = None
    approval_state: str
    diff_summary: str | None = None
