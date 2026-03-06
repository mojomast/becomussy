"""
becomussy – database initialisation helpers.
"""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base, engine

logger = logging.getLogger(__name__)


async def init_db(eng: AsyncEngine | None = None) -> None:
    """Create all tables that don't yet exist.

    In production we rely on Alembic migrations; this helper is a
    convenience for local development and tests.
    """
    eng = eng or engine
    async with eng.begin() as conn:
        # Ensure pgvector extension is available
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Import all models so Base.metadata is populated
        import app.models.audit  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables verified / created.")
