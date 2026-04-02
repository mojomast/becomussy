"""
becomussy – Memory API endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, Role, get_current_user, require_role
from app.db.base import get_session
from app.schemas.common import PaginatedResponse
from app.schemas.memory import (
    MemoryContradictRequest,
    MemoryItemCreate,
    MemoryItemRead,
    MemoryItemUpdate,
    MemoryLinkCreate,
    MemoryLinkRead,
    MemoryReinforceRequest,
    MemorySearchParams,
)
from app.services.memory import MemoryService

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post(
    "",
    response_model=MemoryItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a memory item",
)
async def create_memory(
    data: MemoryItemCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> MemoryItemRead:
    """Create a new memory item."""
    item = await MemoryService.create(session, data, user)
    return MemoryItemRead.model_validate(item)


@router.get(
    "/search",
    response_model=PaginatedResponse[MemoryItemRead],
    summary="Search memory items",
)
async def search_memory(
    q: str | None = Query(None, description="Full-text search in summary and statement"),
    memory_type: str | None = Query(None, description="Filter by memory type"),
    date_from: str | None = Query(None, description="Filter memories from this date (ISO 8601)"),
    date_to: str | None = Query(None, description="Filter memories up to this date (ISO 8601)"),
    project_id: uuid.UUID | None = Query(None, description="Filter by project_id in metadata"),
    person: str | None = Query(None, description="Filter by person in metadata"),
    identity_theme: str | None = Query(None, description="Filter by identity_theme in metadata"),
    confidence: str | None = Query(None, description="Filter by confidence level"),
    approval_state: str | None = Query(None, description="Filter by approval state"),
    item_status: str | None = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[MemoryItemRead]:
    """Search/filter memory items with pagination."""
    from datetime import datetime

    from app.schemas.common import (
        ApprovalStateEnum,
        ConfidenceLevelEnum,
        MemoryTypeEnum,
        StatusEnum,
    )

    params = MemorySearchParams(
        q=q,
        memory_type=MemoryTypeEnum(memory_type) if memory_type else None,
        date_from=datetime.fromisoformat(date_from) if date_from else None,
        date_to=datetime.fromisoformat(date_to) if date_to else None,
        project_id=project_id,
        person=person,
        identity_theme=identity_theme,
        confidence=ConfidenceLevelEnum(confidence) if confidence else None,
        approval_state=ApprovalStateEnum(approval_state) if approval_state else None,
        status=StatusEnum(item_status) if item_status else None,
        limit=limit,
        offset=offset,
    )

    items, total = await MemoryService.search(session, params)

    return PaginatedResponse[MemoryItemRead](
        items=[MemoryItemRead.model_validate(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{memory_id}",
    response_model=MemoryItemRead,
    summary="Get a memory item",
)
async def get_memory(
    memory_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> MemoryItemRead:
    """Retrieve a single memory item by ID."""
    item = await MemoryService.get(session, memory_id)
    return MemoryItemRead.model_validate(item)


@router.patch(
    "/{memory_id}",
    response_model=MemoryItemRead,
    summary="Update a memory item",
)
async def update_memory(
    memory_id: uuid.UUID,
    data: MemoryItemUpdate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> MemoryItemRead:
    """Partially update a memory item."""
    item = await MemoryService.update(session, memory_id, data, user)
    return MemoryItemRead.model_validate(item)


@router.post(
    "/{memory_id}/reinforce",
    response_model=MemoryItemRead,
    summary="Reinforce a memory",
)
async def reinforce_memory(
    memory_id: uuid.UUID,
    data: MemoryReinforceRequest,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> MemoryItemRead:
    """Reinforce a memory by bumping its salience score."""
    item = await MemoryService.reinforce(
        session, memory_id, data.reason, data.source_ref, user
    )
    return MemoryItemRead.model_validate(item)


@router.post(
    "/{memory_id}/contradict",
    response_model=MemoryLinkRead,
    status_code=201,
    summary="Record a contradiction",
)
async def contradict_memory(
    memory_id: uuid.UUID,
    data: MemoryContradictRequest,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> MemoryLinkRead:
    """Record a contradiction between two memory items."""
    link = await MemoryService.contradict(
        session, memory_id, data.contradicting_memory_id, data.reason, user
    )
    return MemoryLinkRead.model_validate(link)
