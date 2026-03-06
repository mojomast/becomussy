"""
becomussy – Project API endpoints.

Includes project CRUD and project-scoped commitment endpoints.
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
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from app.services.projects import CommitmentService, ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


# ── Project CRUD ───────────────────────────────────────────────────────


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
async def create_project(
    data: ProjectCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> ProjectRead:
    """Create a new project."""
    project = await ProjectService.create(session, data, user)
    return ProjectRead.model_validate(project)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectRead],
    summary="List projects",
)
async def list_projects(
    project_status: str | None = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[ProjectRead]:
    """List projects with optional status filter."""
    items, total = await ProjectService.list(
        session,
        status_filter=project_status,
        limit=limit,
        offset=offset,
    )

    return PaginatedResponse[ProjectRead](
        items=[ProjectRead.model_validate(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get a project",
)
async def get_project(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> ProjectRead:
    """Retrieve a single project by ID."""
    project = await ProjectService.get(session, project_id)
    return ProjectRead.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Update a project",
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> ProjectRead:
    """Partially update a project."""
    project = await ProjectService.update(session, project_id, data, user)
    return ProjectRead.model_validate(project)


# ── Project-scoped commitment endpoints ────────────────────────────────


@router.post(
    "/{project_id}/commitments",
    response_model=CommitmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a commitment for a project",
)
async def create_project_commitment(
    project_id: uuid.UUID,
    data: CommitmentCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> CommitmentRead:
    """Create a new commitment under a specific project."""
    # Override the project_id from the URL path
    data.project_id = project_id
    commitment = await CommitmentService.create(session, data, user)
    return CommitmentRead.model_validate(commitment)


@router.get(
    "/{project_id}/commitments",
    response_model=PaginatedResponse[CommitmentRead],
    summary="List commitments for a project",
)
async def list_project_commitments(
    project_id: uuid.UUID,
    commitment_status: str | None = Query(None, alias="status", description="Filter by status"),
    overdue: bool | None = Query(None, description="Filter overdue commitments"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[CommitmentRead]:
    """List commitments for a specific project."""
    # Ensure the project exists
    await ProjectService.get(session, project_id)

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
