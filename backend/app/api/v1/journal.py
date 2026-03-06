"""
becomussy – Journal API endpoints.

CRUD, search, and summarization for journal entries.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, get_current_user
from app.db.base import get_session
from app.schemas.common import PaginatedResponse
from app.schemas.journal import (
    JournalEntryCreate,
    JournalEntryRead,
    JournalEntryUpdate,
    JournalSummarizeRequest,
)
from app.services.journal import JournalService

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.post(
    "",
    response_model=JournalEntryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a journal entry",
)
async def create_journal_entry(
    data: JournalEntryCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> JournalEntryRead:
    """Create a new journal entry."""
    entry = await JournalService.create(session, data, actor=user.user_id)
    return JournalEntryRead.model_validate(entry)


@router.get(
    "/search",
    response_model=PaginatedResponse[JournalEntryRead],
    summary="Search journal entries",
)
async def search_journal_entries(
    keyword: str | None = Query(None, description="Search in title and body"),
    entry_type: str | None = Query(None, description="Filter by entry type"),
    date_from: datetime | None = Query(None, description="Start of date range"),
    date_to: datetime | None = Query(None, description="End of date range"),
    linked_project_id: uuid.UUID | None = Query(
        None, description="Filter by linked project"
    ),
    linked_theme: str | None = Query(
        None, description="Filter by linked identity theme"
    ),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse[JournalEntryRead]:
    """Search journal entries with optional filters."""
    from app.schemas.journal import JournalSearchParams

    params = JournalSearchParams(
        keyword=keyword,
        entry_type=entry_type,
        date_from=date_from,
        date_to=date_to,
        linked_project_id=linked_project_id,
        linked_theme=linked_theme,
        limit=limit,
        offset=offset,
    )
    return await JournalService.search(session, params)


@router.get(
    "/{journal_id}",
    response_model=JournalEntryRead,
    summary="Get a journal entry",
)
async def get_journal_entry(
    journal_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> JournalEntryRead:
    """Retrieve a single journal entry by ID."""
    entry = await JournalService.get(session, journal_id)
    return JournalEntryRead.model_validate(entry)


@router.patch(
    "/{journal_id}",
    response_model=JournalEntryRead,
    summary="Update a journal entry",
)
async def update_journal_entry(
    journal_id: uuid.UUID,
    data: JournalEntryUpdate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> JournalEntryRead:
    """Partially update a journal entry."""
    entry = await JournalService.update(
        session, journal_id, data, actor=user.user_id
    )
    return JournalEntryRead.model_validate(entry)


@router.post(
    "/summarize",
    response_model=list[JournalEntryRead],
    summary="Summarize journal entries in a date range",
)
async def summarize_journal_entries(
    data: JournalSummarizeRequest,
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> list[JournalEntryRead]:
    """Return journal entries in the given range.

    For MVP, returns the raw entries. AI-powered summarization is post-MVP.
    """
    return await JournalService.summarize(
        session,
        range_start=data.range_start,
        range_end=data.range_end,
        summary_type=data.summary_type,
    )
