"""
becomussy – Revision service.

Manages revision proposals with auto risk classification, stage transitions,
and policy-based approval gating.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revision import RevisionProposal
from app.schemas.revision import RevisionProposalCreate, RevisionProposalUpdate
from app.services.audit import AuditService


# ── Risk classification keywords ────────────────────────────────────────

_HIGH_RISK_KEYWORDS = {"constrained", "constraint", "value", "values", "boundary"}
_DESCRIPTIVE_KEYWORDS = {"descriptive", "description", "trait", "tendency"}


def _classify_risk(revision_type: str, target_entity_type: str) -> str:
    """Determine risk class based on revision type and target entity.

    Rules from spec:
    - self_model + constrained/value keywords -> high
    - self_model + descriptive keywords -> medium
    - thread or project target -> low
    - Default: medium
    """
    revision_lower = revision_type.lower()
    target_lower = target_entity_type.lower()

    if target_lower in ("thread", "project"):
        return "low"

    if target_lower == "self_model":
        # Check for high-risk keywords in the revision type
        if any(kw in revision_lower for kw in _HIGH_RISK_KEYWORDS):
            return "high"
        # Check for descriptive keywords
        if any(kw in revision_lower for kw in _DESCRIPTIVE_KEYWORDS):
            return "medium"

    # Default
    return "medium"


def _determine_policy(risk_class: str) -> str:
    """Determine the policy result based on risk classification.

    Low risk -> auto_approve, medium/high -> approval_required.
    """
    if risk_class == "low":
        return "auto_approve"
    return "approval_required"


class RevisionService:
    """Service layer for revision proposal operations."""

    @staticmethod
    async def create(
        session: AsyncSession,
        data: RevisionProposalCreate,
        actor: str,
    ) -> RevisionProposal:
        """Create a new revision proposal with auto-classified risk.

        Sets initial stage to 'observation', classifies risk, and
        determines policy_result based on the risk class.
        """
        risk_class = _classify_risk(data.revision_type, data.target_entity_type)
        policy_result = _determine_policy(risk_class)

        # For low risk auto-approved proposals, set approval_state accordingly
        initial_approval_state = (
            "not_required" if policy_result == "auto_approve" else "pending"
        )

        proposal = RevisionProposal(
            id=uuid.uuid4(),
            revision_type=data.revision_type,
            target_entity_type=data.target_entity_type,
            target_entity_id=data.target_entity_id,
            stage="observation",
            risk_class=risk_class,
            policy_result=policy_result,
            summary=data.summary,
            rationale=data.rationale,
            evidence_json=data.evidence_links,
            proposed_diff_json=data.proposed_diff,
            approval_state=initial_approval_state,
            created_by=actor,
            updated_by=actor,
        )
        session.add(proposal)
        await session.flush()

        await AuditService.log_event(
            session,
            event_type="self_model_revision_proposed",
            entity_type="revision_proposal",
            entity_id=proposal.id,
            actor=actor,
            actor_type="user",
            after_json=_proposal_to_dict(proposal),
            rationale=data.rationale,
            approval_state=initial_approval_state,
        )

        return proposal

    @staticmethod
    async def get(
        session: AsyncSession,
        proposal_id: uuid.UUID,
    ) -> RevisionProposal:
        """Retrieve a single revision proposal or raise 404."""
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

    @staticmethod
    async def list_pending(
        session: AsyncSession,
    ) -> list[RevisionProposal]:
        """Return all proposals with approval_state='pending'."""
        result = await session.execute(
            select(RevisionProposal)
            .where(RevisionProposal.approval_state == "pending")
            .order_by(RevisionProposal.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_stage(
        session: AsyncSession,
        proposal_id: uuid.UUID,
        new_stage: str,
        actor: str,
    ) -> RevisionProposal:
        """Transition a proposal to a new stage and log audit event."""
        proposal = await RevisionService.get(session, proposal_id)
        before = _proposal_to_dict(proposal)

        old_stage = proposal.stage
        proposal.stage = new_stage
        proposal.updated_by = actor
        await session.flush()

        await AuditService.log_event(
            session,
            event_type="revision_stage_changed",
            entity_type="revision_proposal",
            entity_id=proposal.id,
            actor=actor,
            actor_type="user",
            before_json=before,
            after_json=_proposal_to_dict(proposal),
            rationale=f"Stage transition: {old_stage} -> {new_stage}",
        )

        return proposal

    @staticmethod
    async def update(
        session: AsyncSession,
        proposal_id: uuid.UUID,
        data: RevisionProposalUpdate,
        actor: str,
    ) -> RevisionProposal:
        """Partially update a revision proposal."""
        proposal = await RevisionService.get(session, proposal_id)
        before = _proposal_to_dict(proposal)

        update_data = data.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(proposal, field_name, value)

        proposal.updated_by = actor
        await session.flush()

        await AuditService.log_event(
            session,
            event_type="revision_proposal_updated",
            entity_type="revision_proposal",
            entity_id=proposal.id,
            actor=actor,
            actor_type="user",
            before_json=before,
            after_json=_proposal_to_dict(proposal),
        )

        return proposal


def _proposal_to_dict(proposal: RevisionProposal) -> dict[str, Any]:
    """Serialize a RevisionProposal to a plain dict for audit logging."""
    return {
        "id": str(proposal.id),
        "revision_type": proposal.revision_type,
        "target_entity_type": proposal.target_entity_type,
        "target_entity_id": str(proposal.target_entity_id)
        if proposal.target_entity_id
        else None,
        "stage": proposal.stage,
        "risk_class": proposal.risk_class,
        "policy_result": proposal.policy_result,
        "summary": proposal.summary,
        "rationale": proposal.rationale,
        "evidence_json": proposal.evidence_json,
        "simulation_json": proposal.simulation_json,
        "proposed_diff_json": proposal.proposed_diff_json,
        "approval_state": proposal.approval_state,
        "monitoring_plan_json": proposal.monitoring_plan_json,
        "created_by": proposal.created_by,
        "updated_by": proposal.updated_by,
    }
