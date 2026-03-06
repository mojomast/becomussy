"""
becomussy – health-check endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Simple liveness probe."""
    return {"status": "ok", "service": "becoming-system"}
