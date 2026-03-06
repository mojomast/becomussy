"""
becomussy – Revision Proposal Pydantic schemas.

Request/response models for revision proposals with auto-classification.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Create ──────────────────────────────────────────────────────────────


class RevisionProposalCreate(BaseModel):
    """Payload for creating a new revision proposal.

    The service will auto-classify risk_class, set the initial stage
    to 'observation', and determine policy_result based on risk.
    """

    model_config = ConfigDict(extra="forbid")

    revision_type: str
    target_entity_type: str
    target_entity_id: uuid.UUID | None = None
    summary: str
    rationale: str | None = None
    evidence_links: list[Any] = Field(default_factory=list)
    proposed_diff: dict[str, Any] = Field(default_factory=dict)


# ── Read ────────────────────────────────────────────────────────────────


class RevisionProposalRead(BaseModel):
    """Full revision proposal returned from reads."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    revision_type: str
    target_entity_type: str
    target_entity_id: uuid.UUID | None = None
    stage: str
    risk_class: str
    policy_result: str
    summary: str
    rationale: str | None = None
    evidence_json: list[Any] | dict[str, Any] = Field(default_factory=list)
    simulation_json: dict[str, Any] = Field(default_factory=dict)
    proposed_diff_json: dict[str, Any] = Field(default_factory=dict)
    approval_state: str
    monitoring_plan_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str


# ── Update ──────────────────────────────────────────────────────────────


class RevisionProposalUpdate(BaseModel):
    """Payload for updating a revision proposal (partial)."""

    model_config = ConfigDict(extra="forbid")

    stage: str | None = None
    rationale: str | None = None
    evidence_json: list[Any] | None = None
    simulation_json: dict[str, Any] | None = None
