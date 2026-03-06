"""
becomussy – audit log endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, Role, require_role
from app.db.base import get_session
from app.models.audit import AuditEvent
from app.schemas.common import AuditEventRead, PaginatedResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get(
    "",
    response_model=PaginatedResponse[AuditEventRead],
    summary="List audit events",
)
async def list_audit_events(
    entity_type: str | None = Query(None, description="Filter by entity type"),
    entity_id: uuid.UUID | None = Query(None, description="Filter by entity id"),
    event_type: str | None = Query(None, description="Filter by event type"),
    actor: str | None = Query(None, description="Filter by actor"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(require_role(Role.admin, Role.steward, Role.observer)),
) -> PaginatedResponse[AuditEventRead]:
    """Return paginated audit events with optional filters."""
    query = select(AuditEvent)
    count_query = select(func.count()).select_from(AuditEvent)

    # Apply filters
    if entity_type is not None:
        query = query.where(AuditEvent.entity_type == entity_type)
        count_query = count_query.where(AuditEvent.entity_type == entity_type)
    if entity_id is not None:
        query = query.where(AuditEvent.entity_id == entity_id)
        count_query = count_query.where(AuditEvent.entity_id == entity_id)
    if event_type is not None:
        query = query.where(AuditEvent.event_type == event_type)
        count_query = count_query.where(AuditEvent.event_type == event_type)
    if actor is not None:
        query = query.where(AuditEvent.actor == actor)
        count_query = count_query.where(AuditEvent.actor == actor)

    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(AuditEvent.occurred_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    rows = result.scalars().all()

    return PaginatedResponse[AuditEventRead](
        items=[AuditEventRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{audit_id}",
    response_model=AuditEventRead,
    summary="Get a single audit event",
)
async def get_audit_event(
    audit_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(require_role(Role.admin, Role.steward, Role.observer)),
) -> AuditEventRead:
    """Return a single audit event by ID."""
    result = await session.execute(
        select(AuditEvent).where(AuditEvent.id == audit_id)
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit event {audit_id} not found",
        )
    return AuditEventRead.model_validate(event)
