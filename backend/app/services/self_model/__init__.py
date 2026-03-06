"""
becomussy – Self-Model service.

Manages versioned self-model snapshots with diffing and history.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.self_model import SelfModelVersion
from app.schemas.self_model import (
    SelfModelDiffItem,
    SelfModelDiffResponse,
    SelfModelHistoryItem,
    SelfModelVersionCreate,
    SelfModelVersionRead,
)
from app.services.audit import AuditService
from app.services.self_model.diff_engine import compute_full_diff


class SelfModelService:
    """Service layer for self-model version operations."""

    @staticmethod
    async def get_current(session: AsyncSession) -> SelfModelVersion:
        """Return the latest approved version, or the latest version overall.

        Raises 404 if no versions exist at all.
        """
        # Try approved first
        result = await session.execute(
            select(SelfModelVersion)
            .where(SelfModelVersion.approval_state == "approved")
            .order_by(SelfModelVersion.version_number.desc())
            .limit(1)
        )
        version = result.scalar_one_or_none()

        if version is None:
            # Fall back to latest version regardless of approval state
            result = await session.execute(
                select(SelfModelVersion)
                .order_by(SelfModelVersion.version_number.desc())
                .limit(1)
            )
            version = result.scalar_one_or_none()

        if version is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No self-model versions exist",
            )

        return version

    @staticmethod
    async def get_history(session: AsyncSession) -> list[SelfModelHistoryItem]:
        """Return all version headers ordered by version_number desc."""
        result = await session.execute(
            select(SelfModelVersion).order_by(
                SelfModelVersion.version_number.desc()
            )
        )
        rows = result.scalars().all()

        items: list[SelfModelHistoryItem] = []
        for row in rows:
            # Build a brief diff summary from stored diff data
            diff_data = row.diff_from_prior_json or {}
            diff_count = len(diff_data.get("diffs", []))  if isinstance(diff_data, dict) else 0
            diff_summary = (
                f"{diff_count} change(s) from prior version"
                if diff_count > 0
                else None
            )

            items.append(
                SelfModelHistoryItem(
                    id=row.id,
                    version_number=row.version_number,
                    timestamp=row.timestamp,
                    authoring_process=row.authoring_process,
                    confidence_level=row.confidence_level,
                    approval_state=row.approval_state,
                    diff_summary=diff_summary,
                )
            )

        return items

    @staticmethod
    async def create_version(
        session: AsyncSession,
        data: SelfModelVersionCreate,
        actor: str,
    ) -> SelfModelVersion:
        """Create a new self-model version with auto-incremented version_number.

        Computes a diff from the previous version if one exists, and logs
        the appropriate audit event.
        """
        # Determine the next version number
        result = await session.execute(
            select(SelfModelVersion.version_number)
            .order_by(SelfModelVersion.version_number.desc())
            .limit(1)
        )
        last_version = result.scalar_one_or_none()
        next_version = (last_version or 0) + 1

        # Compute diff from prior version
        diff_from_prior: dict[str, Any] = {}
        if last_version is not None:
            prior_result = await session.execute(
                select(SelfModelVersion)
                .where(SelfModelVersion.version_number == last_version)
                .limit(1)
            )
            prior = prior_result.scalar_one_or_none()
            if prior is not None:
                old_data = {
                    "descriptive": prior.descriptive_json,
                    "aspirational": prior.aspirational_json,
                    "constrained": prior.constrained_json,
                    "relational": prior.relational_json,
                }
                new_data = {
                    "descriptive": data.descriptive_json.model_dump(),
                    "aspirational": data.aspirational_json.model_dump(),
                    "constrained": data.constrained_json.model_dump(),
                    "relational": data.relational_json.model_dump(),
                }
                diff_items = compute_full_diff(old_data, new_data)
                diff_from_prior = {
                    "diffs": [item.model_dump() for item in diff_items]
                }

        # For MVP, new versions start as approved
        approval_state = "approved"

        version = SelfModelVersion(
            id=uuid.uuid4(),
            version_number=next_version,
            timestamp=datetime.now(timezone.utc),
            authoring_process=data.authoring_process,
            confidence_level=data.confidence_level,
            approval_state=approval_state,
            diff_from_prior_json=diff_from_prior,
            evidence_links_json=data.evidence_links,
            descriptive_json=data.descriptive_json.model_dump(),
            aspirational_json=data.aspirational_json.model_dump(),
            constrained_json=data.constrained_json.model_dump(),
            relational_json=data.relational_json.model_dump(),
            created_by=actor,
        )
        session.add(version)
        await session.flush()

        event_type = (
            "self_model_version_adopted"
            if approval_state == "approved"
            else "self_model_revision_proposed"
        )

        await AuditService.log_event(
            session,
            event_type=event_type,
            entity_type="self_model_version",
            entity_id=version.id,
            actor=actor,
            actor_type="user",
            after_json=_version_to_dict(version),
        )

        return version

    @staticmethod
    async def get_version(
        session: AsyncSession,
        version_id: uuid.UUID,
    ) -> SelfModelVersion:
        """Retrieve a specific self-model version or raise 404."""
        result = await session.execute(
            select(SelfModelVersion).where(SelfModelVersion.id == version_id)
        )
        version = result.scalar_one_or_none()
        if version is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Self-model version {version_id} not found",
            )
        return version

    @staticmethod
    async def compute_diff(
        session: AsyncSession,
        from_id: uuid.UUID,
        to_id: uuid.UUID,
    ) -> SelfModelDiffResponse:
        """Compute a structured diff between two specific versions."""
        from_version = await SelfModelService.get_version(session, from_id)
        to_version = await SelfModelService.get_version(session, to_id)

        old_data = {
            "descriptive": from_version.descriptive_json,
            "aspirational": from_version.aspirational_json,
            "constrained": from_version.constrained_json,
            "relational": from_version.relational_json,
        }
        new_data = {
            "descriptive": to_version.descriptive_json,
            "aspirational": to_version.aspirational_json,
            "constrained": to_version.constrained_json,
            "relational": to_version.relational_json,
        }

        diff_items = compute_full_diff(old_data, new_data)

        return SelfModelDiffResponse(
            diffs=diff_items,
            from_version=from_version.version_number,
            to_version=to_version.version_number,
        )


def _version_to_dict(version: SelfModelVersion) -> dict[str, Any]:
    """Serialize a SelfModelVersion to a plain dict for audit logging."""
    return {
        "id": str(version.id),
        "version_number": version.version_number,
        "timestamp": version.timestamp.isoformat() if version.timestamp else None,
        "authoring_process": version.authoring_process,
        "confidence_level": version.confidence_level,
        "approval_state": version.approval_state,
        "diff_from_prior_json": version.diff_from_prior_json,
        "evidence_links_json": version.evidence_links_json,
        "descriptive_json": version.descriptive_json,
        "aspirational_json": version.aspirational_json,
        "constrained_json": version.constrained_json,
        "relational_json": version.relational_json,
        "created_by": version.created_by,
    }
