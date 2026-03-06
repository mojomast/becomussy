"""
becomussy – Governance service.

Provides approval workflows, policy checks, and emergency-freeze controls
for the revision-proposal lifecycle.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.governance import ApprovalDecision
from app.models.revision import RevisionProposal
from app.services.audit import AuditService

# ── Module-level freeze state (MVP in-memory; production would use DB) ──
_freeze_state: dict[str, bool] = {
    "self_model": False,
    "promotions": False,
    "all_revisions": False,
}


class GovernanceService:
    """Static-method service for governance operations."""

    # ─── Pending approvals ──────────────────────────────────────────────

    @staticmethod
    async def get_pending_approvals(
        session: AsyncSession,
    ) -> list[RevisionProposal]:
        """Return revision proposals that are awaiting approval.

        A proposal is "pending" when its approval_state is 'pending' AND it is
        either already in the 'approval' stage or has a medium/high risk class.
        """
        query = (
            select(RevisionProposal)
            .where(RevisionProposal.approval_state == "pending")
            .where(
                (RevisionProposal.stage == "approval")
                | (RevisionProposal.risk_class.in_(["medium", "high"]))
            )
            .order_by(RevisionProposal.created_at.desc())
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    # ─── Approve ────────────────────────────────────────────────────────

    @staticmethod
    async def approve(
        session: AsyncSession,
        proposal_id: uuid.UUID,
        notes: str | None,
        actor: str,
    ) -> ApprovalDecision:
        """Approve a revision proposal and advance it to adoption."""
        proposal = await _load_proposal(session, proposal_id)

        if proposal.approval_state == "approved":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Proposal has already been approved",
            )

        decision = ApprovalDecision(
            id=uuid.uuid4(),
            revision_proposal_id=proposal_id,
            decision="approved",
            decided_by=actor,
            decided_at=datetime.now(timezone.utc),
            notes=notes,
            requested_evidence_json=[],
        )
        session.add(decision)

        # Advance proposal state
        proposal.approval_state = "approved"
        proposal.stage = "adoption"
        proposal.updated_by = actor

        await AuditService.log_event(
            session,
            event_type="self_model_revision_approved",
            entity_type="revision_proposal",
            entity_id=proposal_id,
            actor=actor,
            actor_type="user",
            after_json={
                "decision": "approved",
                "notes": notes,
                "new_stage": "adoption",
            },
            rationale=notes,
            approval_state="approved",
        )

        await session.flush()
        return decision

    # ─── Reject ─────────────────────────────────────────────────────────

    @staticmethod
    async def reject(
        session: AsyncSession,
        proposal_id: uuid.UUID,
        notes: str | None,
        actor: str,
    ) -> ApprovalDecision:
        """Reject a revision proposal and close it."""
        proposal = await _load_proposal(session, proposal_id)

        if proposal.approval_state in ("approved", "rejected"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Proposal has already been {proposal.approval_state}",
            )

        decision = ApprovalDecision(
            id=uuid.uuid4(),
            revision_proposal_id=proposal_id,
            decision="rejected",
            decided_by=actor,
            decided_at=datetime.now(timezone.utc),
            notes=notes,
            requested_evidence_json=[],
        )
        session.add(decision)

        proposal.approval_state = "rejected"
        proposal.stage = "closed"
        proposal.updated_by = actor

        await AuditService.log_event(
            session,
            event_type="self_model_revision_rejected",
            entity_type="revision_proposal",
            entity_id=proposal_id,
            actor=actor,
            actor_type="user",
            after_json={
                "decision": "rejected",
                "notes": notes,
                "new_stage": "closed",
            },
            rationale=notes,
            approval_state="rejected",
        )

        await session.flush()
        return decision

    # ─── Defer ──────────────────────────────────────────────────────────

    @staticmethod
    async def defer(
        session: AsyncSession,
        proposal_id: uuid.UUID,
        notes: str | None,
        requested_evidence: list[str] | None,
        actor: str,
    ) -> ApprovalDecision:
        """Defer a revision proposal back to evidence collection."""
        proposal = await _load_proposal(session, proposal_id)

        if proposal.approval_state in ("approved", "rejected"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot defer a proposal that has been {proposal.approval_state}",
            )

        evidence_list = requested_evidence or []

        decision = ApprovalDecision(
            id=uuid.uuid4(),
            revision_proposal_id=proposal_id,
            decision="deferred",
            decided_by=actor,
            decided_at=datetime.now(timezone.utc),
            notes=notes,
            requested_evidence_json=evidence_list,
        )
        session.add(decision)

        proposal.approval_state = "deferred"
        proposal.stage = "evidence_collection"
        proposal.updated_by = actor

        await AuditService.log_event(
            session,
            event_type="self_model_revision_deferred",
            entity_type="revision_proposal",
            entity_id=proposal_id,
            actor=actor,
            actor_type="user",
            after_json={
                "decision": "deferred",
                "notes": notes,
                "requested_evidence": evidence_list,
                "new_stage": "evidence_collection",
            },
            rationale=notes,
            approval_state="deferred",
        )

        await session.flush()
        return decision

    # ─── Policy check ───────────────────────────────────────────────────

    @staticmethod
    def check_policy(
        risk_class: str,
        revision_type: str,
    ) -> dict[str, Any]:
        """Evaluate governance policy for a risk-class / revision-type pair.

        Policy rules (MVP):
        - low risk:    auto_approve, 0 evidence, no simulation
        - medium risk: approval_required, 2 evidence items, no simulation
        - high risk:   approval_required, 3 evidence items, simulation required
        """
        rules: dict[str, dict[str, Any]] = {
            "low": {
                "approval_required": False,
                "requires_evidence_count": 0,
                "requires_simulation": False,
                "policy": "auto_approve",
            },
            "medium": {
                "approval_required": True,
                "requires_evidence_count": 2,
                "requires_simulation": False,
                "policy": "approval_required",
            },
            "high": {
                "approval_required": True,
                "requires_evidence_count": 3,
                "requires_simulation": True,
                "policy": "approval_required",
            },
        }

        rule = rules.get(risk_class)
        if rule is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown risk_class: {risk_class}. Must be one of: low, medium, high",
            )

        return {
            "risk_class": risk_class,
            "revision_type": revision_type,
            **rule,
        }

    # ─── Freeze controls ───────────────────────────────────────────────

    @staticmethod
    def get_freeze_status() -> dict[str, bool]:
        """Return current state of all emergency-freeze toggles."""
        return {
            "self_model_frozen": _freeze_state["self_model"],
            "promotions_frozen": _freeze_state["promotions"],
            "all_revisions_frozen": _freeze_state["all_revisions"],
        }

    @staticmethod
    async def set_freeze(
        freeze_type: str,
        enabled: bool,
        reason: str,
        actor: str,
        session: AsyncSession,
    ) -> dict[str, bool]:
        """Enable or disable an emergency freeze and log the audit event."""
        if freeze_type not in _freeze_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown freeze_type: {freeze_type}. Must be one of: self_model, promotions, all_revisions",
            )

        _freeze_state[freeze_type] = enabled

        event_type = (
            "emergency_freeze_enabled" if enabled else "emergency_freeze_disabled"
        )
        await AuditService.log_event(
            session,
            event_type=event_type,
            entity_type="system_freeze",
            entity_id=None,
            actor=actor,
            actor_type="user",
            after_json={
                "freeze_type": freeze_type,
                "enabled": enabled,
                "reason": reason,
            },
            rationale=reason,
        )

        await session.flush()
        return GovernanceService.get_freeze_status()

    @staticmethod
    def is_frozen(freeze_type: str) -> bool:
        """Check if a specific freeze type is currently active."""
        return _freeze_state.get(freeze_type, False)


# ── Private helpers ─────────────────────────────────────────────────────


async def _load_proposal(
    session: AsyncSession,
    proposal_id: uuid.UUID,
) -> RevisionProposal:
    """Load a revision proposal by ID or raise 404."""
    result = await session.execute(
        select(RevisionProposal).where(RevisionProposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Revision proposal {proposal_id} not found",
        )
    return proposal
