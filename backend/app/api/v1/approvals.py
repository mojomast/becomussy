"""
becomussy – Approval & governance API endpoints.

Provides endpoints for reviewing pending approvals, rendering decisions
(approve / reject / defer), checking policy rules, and managing emergency
freeze controls.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, Role, require_role
from app.db.base import get_session
from app.schemas.governance import (
    ApprovalDecisionCreate,
    ApprovalDecisionRead,
    FreezeControlRequest,
    FreezeStatus,
    PendingApprovalItem,
)
from app.services.governance import GovernanceService

router = APIRouter(prefix="/approvals", tags=["Approvals"])


# ── Pending approvals ───────────────────────────────────────────────────


@router.get(
    "/pending",
    response_model=list[PendingApprovalItem],
    summary="List pending approvals",
)
async def list_pending_approvals(
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(
        require_role(Role.steward, Role.admin, Role.reviewer)
    ),
) -> list[PendingApprovalItem]:
    """Return all revision proposals currently awaiting governance approval."""
    proposals = await GovernanceService.get_pending_approvals(session)
    return [PendingApprovalItem.model_validate(p) for p in proposals]


# ── Approve ─────────────────────────────────────────────────────────────


@router.post(
    "/{proposal_id}/approve",
    response_model=ApprovalDecisionRead,
    summary="Approve a revision proposal",
)
async def approve_proposal(
    proposal_id: uuid.UUID,
    body: ApprovalDecisionCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(require_role(Role.steward, Role.admin)),
) -> ApprovalDecisionRead:
    """Approve a revision proposal and advance it to the adoption stage."""
    decision = await GovernanceService.approve(
        session=session,
        proposal_id=proposal_id,
        notes=body.notes,
        actor=user.user_id,
    )
    return ApprovalDecisionRead.model_validate(decision)


# ── Reject ──────────────────────────────────────────────────────────────


@router.post(
    "/{proposal_id}/reject",
    response_model=ApprovalDecisionRead,
    summary="Reject a revision proposal",
)
async def reject_proposal(
    proposal_id: uuid.UUID,
    body: ApprovalDecisionCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(require_role(Role.steward, Role.admin)),
) -> ApprovalDecisionRead:
    """Reject a revision proposal and close it."""
    decision = await GovernanceService.reject(
        session=session,
        proposal_id=proposal_id,
        notes=body.notes,
        actor=user.user_id,
    )
    return ApprovalDecisionRead.model_validate(decision)


# ── Defer ───────────────────────────────────────────────────────────────


@router.post(
    "/{proposal_id}/defer",
    response_model=ApprovalDecisionRead,
    summary="Defer a revision proposal for more evidence",
)
async def defer_proposal(
    proposal_id: uuid.UUID,
    body: ApprovalDecisionCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(require_role(Role.steward, Role.admin)),
) -> ApprovalDecisionRead:
    """Defer a revision proposal back to evidence collection."""
    decision = await GovernanceService.defer(
        session=session,
        proposal_id=proposal_id,
        notes=body.notes,
        requested_evidence=body.requested_evidence,
        actor=user.user_id,
    )
    return ApprovalDecisionRead.model_validate(decision)


# ── Policy check ────────────────────────────────────────────────────────


@router.get(
    "/policy/check",
    summary="Check governance policy for a risk/revision combination",
)
async def check_policy(
    risk_class: str = Query(
        ..., description="Risk classification: low, medium, high"
    ),
    revision_type: str = Query(
        ..., description="Type of revision (e.g. belief, value, trait)"
    ),
    _user: CurrentUser = Depends(
        require_role(Role.steward, Role.admin, Role.reviewer, Role.agent_runtime)
    ),
) -> dict:
    """Return the governance policy for the given risk class and revision type."""
    return GovernanceService.check_policy(risk_class, revision_type)


# ── Freeze status ───────────────────────────────────────────────────────


@router.get(
    "/freeze",
    response_model=FreezeStatus,
    summary="Get current freeze status",
)
async def get_freeze_status(
    _user: CurrentUser = Depends(
        require_role(
            Role.steward, Role.admin, Role.reviewer, Role.agent_runtime, Role.observer
        )
    ),
) -> FreezeStatus:
    """Return current state of all emergency freeze toggles."""
    return FreezeStatus(**GovernanceService.get_freeze_status())


@router.post(
    "/freeze",
    response_model=FreezeStatus,
    summary="Set emergency freeze control",
)
async def set_freeze(
    body: FreezeControlRequest,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(require_role(Role.steward, Role.admin)),
) -> FreezeStatus:
    """Enable or disable an emergency freeze."""
    result = await GovernanceService.set_freeze(
        freeze_type=body.freeze_type,
        enabled=body.enabled,
        reason=body.reason,
        actor=user.user_id,
        session=session,
    )
    return FreezeStatus(**result)
