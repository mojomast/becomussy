"""
becomussy – Audit service.

Provides the core ``log_event`` helper used by every other service to record
immutable audit trail entries.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditEvent


class AuditService:
    """Thin service layer over the audit_events table."""

    @staticmethod
    async def log_event(
        session: AsyncSession,
        *,
        event_type: str,
        entity_type: str,
        entity_id: uuid.UUID | None = None,
        actor: str,
        actor_type: str,
        before_json: dict[str, Any] | None = None,
        after_json: dict[str, Any] | None = None,
        rationale: str | None = None,
        provenance_json: dict[str, Any] | None = None,
        approval_state: str | None = None,
    ) -> AuditEvent:
        """Create and flush a new ``AuditEvent`` row.

        The caller is responsible for committing the transaction (or the
        FastAPI session dependency will commit automatically).
        """
        event = AuditEvent(
            id=uuid.uuid4(),
            occurred_at=datetime.now(timezone.utc),
            actor=actor,
            actor_type=actor_type,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            before_json=before_json,
            after_json=after_json,
            rationale=rationale,
            provenance_json=provenance_json or {},
            approval_state=approval_state,
        )
        session.add(event)
        await session.flush()
        return event
