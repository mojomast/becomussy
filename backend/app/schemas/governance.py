"""
becomussy – Governance Pydantic schemas (v2).

Covers approval decisions, pending-approval views, freeze controls,
and policy-rule definitions.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Approval Decision schemas ───────────────────────────────────────────


class ApprovalDecisionCreate(BaseModel):
    """Payload for creating an approval decision (approve / reject / defer)."""

    model_config = ConfigDict(extra="forbid")

    decision: str = Field(
        ...,
        description="One of: approved, rejected, deferred",
        pattern=r"^(approved|rejected|deferred)$",
    )
    notes: str | None = Field(None, description="Optional notes from the reviewer")
    requested_evidence: list[str] | None = Field(
        None,
        description="Optional list of additional evidence types requested (for deferral)",
    )


class ApprovalDecisionRead(BaseModel):
    """Read-only representation of an approval decision record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    revision_proposal_id: uuid.UUID
    decision: str
    decided_by: str
    decided_at: datetime
    notes: str | None = None
    requested_evidence_json: list[Any] = Field(default_factory=list)
    immutable: bool = True


# ── Pending-approval view ───────────────────────────────────────────────


class PendingApprovalItem(BaseModel):
    """Lightweight view of a revision proposal awaiting approval."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    revision_type: str
    target_entity_type: str
    summary: str
    risk_class: str
    stage: str
    evidence_json: list[Any] | dict[str, Any] = Field(default_factory=list)
    created_at: datetime
    created_by: str


# ── Freeze-control schemas ──────────────────────────────────────────────


class FreezeControlRequest(BaseModel):
    """Request to enable or disable an emergency freeze."""

    model_config = ConfigDict(extra="forbid")

    freeze_type: str = Field(
        ...,
        description="One of: self_model, promotions, all_revisions",
        pattern=r"^(self_model|promotions|all_revisions)$",
    )
    reason: str = Field(..., min_length=1, description="Reason for the freeze change")
    enabled: bool = Field(..., description="True to freeze, False to unfreeze")


class FreezeStatus(BaseModel):
    """Current state of all emergency freeze toggles."""

    self_model_frozen: bool = False
    promotions_frozen: bool = False
    all_revisions_frozen: bool = False


# ── Policy-rule schema ──────────────────────────────────────────────────


class PolicyRule(BaseModel):
    """Declarative policy rule for a given revision / risk combination."""

    revision_type: str
    risk_class: str
    policy: str = Field(
        ...,
        description="One of: auto_approve, approval_required",
        pattern=r"^(auto_approve|approval_required)$",
    )
    allowed_actors: list[str] = Field(default_factory=list)
    requires_evidence_count: int = Field(0, ge=0)
    requires_simulation: bool = False
