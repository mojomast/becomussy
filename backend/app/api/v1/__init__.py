"""
becomussy – API v1 router aggregate.

Every domain sub-router is included here.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.approvals import router as approvals_router
from app.api.v1.audit import router as audit_router
from app.api.v1.commitments import router as commitments_router
from app.api.v1.continuity import router as continuity_router
from app.api.v1.health import router as health_router
from app.api.v1.journal import router as journal_router
from app.api.v1.memory import router as memory_router
from app.api.v1.projects import router as projects_router
from app.api.v1.self_model import router as self_model_router
from app.api.v1.threads import router as threads_router

router = APIRouter()

# ── Sub-routers ─────────────────────────────────────────────────────────
router.include_router(health_router)
router.include_router(audit_router)
router.include_router(memory_router)
router.include_router(threads_router)
router.include_router(projects_router)
router.include_router(commitments_router)
router.include_router(journal_router)
router.include_router(self_model_router)
router.include_router(continuity_router)
router.include_router(approvals_router)
