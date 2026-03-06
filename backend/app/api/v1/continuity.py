"""
becomussy – Continuity API endpoints.

Provides the /resume endpoint that returns a compiled resume bundle
for the agent runtime's continuity layer, plus a /resume/debug
endpoint for steward inspection.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, Role, get_current_user, require_role
from app.db.base import get_session
from app.schemas.continuity import ResumeBundle
from app.services.search.context_compiler import ContextCompiler

router = APIRouter(prefix="/continuity", tags=["Continuity"])


@router.get(
    "/resume",
    response_model=ResumeBundle,
    summary="Get resume bundle",
    description=(
        "Compile and return a resume bundle — a structured snapshot of "
        "active threads, urgent commitments, recent identity changes, "
        "active projects, and relevant memories. Used by the agent "
        "runtime to re-establish continuity at the start of each session."
    ),
)
async def get_resume_bundle(
    query: str | None = Query(
        default=None,
        description="Optional search query to bias memory retrieval.",
    ),
    token_budget: int = Query(
        default=4000,
        ge=500,
        le=32000,
        description="Rough token budget controlling items per section.",
    ),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(get_current_user),
) -> ResumeBundle:
    """Compile and return a resume bundle."""
    bundle = await ContextCompiler.compile_resume_bundle(
        session=session,
        query=query,
        token_budget=token_budget,
    )
    # Strip debug_info for non-steward/admin callers
    if _user.role not in (Role.steward, Role.admin):
        bundle.debug_info = None
    return bundle


@router.get(
    "/resume/debug",
    response_model=ResumeBundle,
    summary="Get resume bundle with debug info",
    description=(
        "Same as GET /resume but always includes debug_info with "
        "selection metadata and counts. Restricted to steward and admin roles."
    ),
)
async def get_resume_bundle_debug(
    query: str | None = Query(
        default=None,
        description="Optional search query to bias memory retrieval.",
    ),
    token_budget: int = Query(
        default=4000,
        ge=500,
        le=32000,
        description="Rough token budget controlling items per section.",
    ),
    session: AsyncSession = Depends(get_session),
    _user: CurrentUser = Depends(require_role(Role.steward, Role.admin)),
) -> ResumeBundle:
    """Compile and return a resume bundle with debug info (steward/admin only)."""
    return await ContextCompiler.compile_resume_bundle(
        session=session,
        query=query,
        token_budget=token_budget,
    )
