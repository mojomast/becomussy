"""
becomussy – Commitment API endpoints (top-level).

Provides commitment CRUD independent of project context.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, get_current_user
from app.db.base import get_session
from app.schemas.common import PaginatedResponse, StatusEnum
from app.schemas.project import (
    CommitmentCreate,
    CommitmentRead,
    CommitmentSearchParams,
    CommitmentUpdate,
)
from app.services.projects import CommitmentService

router = APIRouter(prefix="/commitments", tags=["Commitments"])


@router.post(
    "",
    response_model=CommitmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a commitment",
)
async def create_commitment(
    data: CommitmentCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> CommitmentRead:
    """Create a new commitment (optionally linked to a project)."""
    commitment = await CommitmentService.create(session, data, user)
    return CommitmentRead.model_validate(commitment)


@router.get(
    "",
    response_model=PaginatedResponse[CommitmentRead],
    summary="List all commitments",
)
async def list_commitments(
    project_id: uuid.UUID | None = Query(None, description="Filter by project ID"),
    commitment_status: str | None = Query(None, alias="status", description="Filter by status"),
    overdue: bool | None = Query(None, description="Filter overdue commitments"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[CommitmentRead]:
    """List all commitments with optional filters."""
    params = CommitmentSearchParams(
        project_id=project_id,
        status=StatusEnum(commitment_status) if commitment_status else None,
        overdue=overdue,
        limit=limit,
        offset=offset,
    )

    items, total = await CommitmentService.list(session, params)

    return PaginatedResponse[CommitmentRead](
        items=[CommitmentRead.model_validate(c) for c in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{commitment_id}",
    response_model=CommitmentRead,
    summary="Get a commitment",
)
async def get_commitment(
    commitment_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> CommitmentRead:
    """Retrieve a single commitment by ID."""
    commitment = await CommitmentService.get(session, commitment_id)
    return CommitmentRead.model_validate(commitment)


@router.patch(
    "/{commitment_id}",
    response_model=CommitmentRead,
    summary="Update a commitment",
)
async def update_commitment(
    commitment_id: uuid.UUID,
    data: CommitmentUpdate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> CommitmentRead:
    """Partially update a commitment."""
    commitment = await CommitmentService.update(session, commitment_id, data, user)
    return CommitmentRead.model_validate(commitment)
