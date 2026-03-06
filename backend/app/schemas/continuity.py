"""
becomussy – Continuity & Resume Bundle schemas.

These schemas define the structure of the "context compiler" output:
the resume bundle that gives the agent runtime a quick snapshot of
active threads, commitments, identity changes, and relevant memories.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Request ─────────────────────────────────────────────────────────────


class ResumeBundleRequest(BaseModel):
    """Optional parameters when requesting a resume bundle."""

    model_config = ConfigDict(extra="forbid")

    query: str | None = Field(
        default=None,
        description="Optional search query to bias memory retrieval toward a topic.",
    )
    token_budget: int = Field(
        default=4000,
        ge=500,
        le=32000,
        description="Rough token budget – controls how many items per section.",
    )


# ── Section summaries ───────────────────────────────────────────────────


class ThreadSummary(BaseModel):
    """Condensed view of an active thread."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    thread_type: str | None = None
    status: str
    urgency: int | None = None
    importance: int | None = None
    next_action: str | None = None
    blocker: str | None = None
    updated_at: datetime | None = None


class CommitmentSummary(BaseModel):
    """Condensed view of an urgent or overdue commitment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    commitment_text: str
    made_to: str | None = None
    due_date: datetime | None = None
    status: str
    risk_if_missed: str | None = None
    project_name: str | None = None


class ProjectSummary(BaseModel):
    """Condensed view of an active project."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    purpose: str | None = None
    current_phase: str | None = None
    status: str
    next_steps: list[str] = Field(default_factory=list)


class MemorySummary(BaseModel):
    """Condensed view of a relevant memory item."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    memory_type: str
    summary: str | None = None
    importance_score: float | None = None
    salience_score: float | None = None
    timestamp: datetime | None = None


class IdentityChangeSummary(BaseModel):
    """Condensed view of a recent self-model revision."""

    model_config = ConfigDict(from_attributes=True)

    version_number: int
    timestamp: datetime
    diff_summary: str


# ── Resume Bundle (top-level output) ────────────────────────────────────


class ResumeBundle(BaseModel):
    """
    The full resume bundle returned by the context compiler.

    This is the primary payload consumed by the agent runtime at the
    start of each interaction to re-establish continuity.
    """

    model_config = ConfigDict(extra="forbid")

    top_threads: list[ThreadSummary] = Field(default_factory=list)
    urgent_commitments: list[CommitmentSummary] = Field(default_factory=list)
    recent_identity_changes: list[IdentityChangeSummary] = Field(default_factory=list)
    active_projects: list[ProjectSummary] = Field(default_factory=list)
    relevant_memories: list[MemorySummary] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    recommended_next_actions: list[str] = Field(default_factory=list)
    generated_at: datetime
    token_budget: int
    debug_info: dict[str, Any] | None = None
