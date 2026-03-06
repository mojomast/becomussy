"""
becomussy – Self-Model API endpoints.

Versioned self-model management, diffing, and revision proposal creation.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, get_current_user
from app.db.base import get_session
from app.schemas.revision import RevisionProposalCreate, RevisionProposalRead
from app.schemas.self_model import (
    SelfModelDiffRequest,
    SelfModelDiffResponse,
    SelfModelHistoryItem,
    SelfModelVersionCreate,
    SelfModelVersionRead,
)
from app.services.revisions import RevisionService
from app.services.self_model import SelfModelService

router = APIRouter(prefix="/self-model", tags=["Self-Model"])


@router.get(
    "/current",
    response_model=SelfModelVersionRead,
    summary="Get current self-model version",
)
async def get_current_self_model(
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> SelfModelVersionRead:
    """Return the latest approved self-model version (or latest overall)."""
    version = await SelfModelService.get_current(session)
    return SelfModelVersionRead.model_validate(version)


@router.get(
    "/history",
    response_model=list[SelfModelHistoryItem],
    summary="Get self-model version history",
)
async def get_self_model_history(
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> list[SelfModelHistoryItem]:
    """Return all self-model version headers ordered by version_number desc."""
    return await SelfModelService.get_history(session)


@router.get(
    "/version/{version_id}",
    response_model=SelfModelVersionRead,
    summary="Get a specific self-model version",
)
async def get_self_model_version(
    version_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> SelfModelVersionRead:
    """Retrieve a specific self-model version by ID."""
    version = await SelfModelService.get_version(session, version_id)
    return SelfModelVersionRead.model_validate(version)


@router.post(
    "/version",
    response_model=SelfModelVersionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new self-model version",
)
async def create_self_model_version(
    data: SelfModelVersionCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> SelfModelVersionRead:
    """Create a new self-model version with auto-incremented version number."""
    version = await SelfModelService.create_version(
        session, data, actor=user.user_id
    )
    return SelfModelVersionRead.model_validate(version)


@router.post(
    "/diff",
    response_model=SelfModelDiffResponse,
    summary="Compute diff between two versions",
)
async def compute_self_model_diff(
    data: SelfModelDiffRequest,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> SelfModelDiffResponse:
    """Compute a structured diff between two self-model versions."""
    return await SelfModelService.compute_diff(
        session, from_id=data.from_version_id, to_id=data.to_version_id
    )


@router.post(
    "/revision-proposal",
    response_model=RevisionProposalRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a revision proposal",
)
async def create_revision_proposal(
    data: RevisionProposalCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> RevisionProposalRead:
    """Create a new revision proposal (delegates to RevisionService)."""
    proposal = await RevisionService.create(session, data, actor=user.user_id)
    return RevisionProposalRead.model_validate(proposal)
