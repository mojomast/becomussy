"""
becomussy – Thread API endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, get_current_user
from app.db.base import get_session
from app.schemas.common import PaginatedResponse, StatusEnum
from app.schemas.thread import (
    ThreadCreate,
    ThreadRead,
    ThreadSearchParams,
    ThreadUpdate,
)
from app.services.threads import ThreadService

router = APIRouter(prefix="/threads", tags=["Threads"])


@router.post(
    "",
    response_model=ThreadRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a thread",
)
async def create_thread(
    data: ThreadCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> ThreadRead:
    """Create a new thread."""
    thread = await ThreadService.create(session, data, user)
    return ThreadRead.model_validate(thread)


@router.get(
    "",
    response_model=PaginatedResponse[ThreadRead],
    summary="List threads",
)
async def list_threads(
    thread_status: str | None = Query(None, alias="status", description="Filter by status"),
    thread_type: str | None = Query(None, description="Filter by thread type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[ThreadRead]:
    """List threads with optional filters."""
    params = ThreadSearchParams(
        status=StatusEnum(thread_status) if thread_status else None,
        thread_type=thread_type,
        limit=limit,
        offset=offset,
    )

    items, total = await ThreadService.list(session, params)

    return PaginatedResponse[ThreadRead](
        items=[ThreadRead.model_validate(t) for t in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{thread_id}",
    response_model=ThreadRead,
    summary="Get a thread",
)
async def get_thread(
    thread_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> ThreadRead:
    """Retrieve a single thread by ID."""
    thread = await ThreadService.get(session, thread_id)
    return ThreadRead.model_validate(thread)


@router.patch(
    "/{thread_id}",
    response_model=ThreadRead,
    summary="Update a thread",
)
async def update_thread(
    thread_id: uuid.UUID,
    data: ThreadUpdate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> ThreadRead:
    """Partially update a thread."""
    thread = await ThreadService.update(session, thread_id, data, user)
    return ThreadRead.model_validate(thread)
