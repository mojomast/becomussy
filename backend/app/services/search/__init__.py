"""
becomussy – Search service.

MVP implementation uses keyword-based ILIKE search on memory_items.
Future versions will add pgvector semantic search.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import MemoryItem


class SearchService:
    """Static methods for searching and retrieving memory items."""

    @staticmethod
    async def search_memories(
        session: AsyncSession,
        query: str | None = None,
        filters: dict[str, Any] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[MemoryItem], int]:
        """
        Keyword-based search over memory_items.

        Parameters
        ----------
        session : AsyncSession
        query : optional search string (matched via ILIKE on summary + statement)
        filters : dict with optional keys:
            memory_type, date_from, date_to, status,
            confidence_level, approval_state
        limit : max results to return
        offset : pagination offset

        Returns
        -------
        (results, total_count)
        """
        filters = filters or {}
        base = select(MemoryItem)
        count_base = select(func.count()).select_from(MemoryItem)

        conditions: list[Any] = []

        # ── Keyword search ──────────────────────────────────────────
        if query:
            pattern = f"%{query}%"
            conditions.append(
                or_(
                    MemoryItem.summary.ilike(pattern),
                    MemoryItem.statement.ilike(pattern),
                )
            )

        # ── Filters ─────────────────────────────────────────────────
        if "memory_type" in filters and filters["memory_type"] is not None:
            conditions.append(MemoryItem.memory_type == filters["memory_type"])

        if "date_from" in filters and filters["date_from"] is not None:
            conditions.append(MemoryItem.timestamp >= filters["date_from"])

        if "date_to" in filters and filters["date_to"] is not None:
            conditions.append(MemoryItem.timestamp <= filters["date_to"])

        if "status" in filters and filters["status"] is not None:
            conditions.append(MemoryItem.status == filters["status"])

        if "confidence_level" in filters and filters["confidence_level"] is not None:
            conditions.append(
                MemoryItem.confidence_level == filters["confidence_level"]
            )

        if "approval_state" in filters and filters["approval_state"] is not None:
            conditions.append(
                MemoryItem.approval_state == filters["approval_state"]
            )

        # ── Apply conditions ────────────────────────────────────────
        if conditions:
            base = base.where(and_(*conditions))
            count_base = count_base.where(and_(*conditions))

        # ── Ordering ────────────────────────────────────────────────
        base = base.order_by(
            MemoryItem.importance_score.desc().nullslast(),
            MemoryItem.created_at.desc(),
        )

        # ── Pagination ──────────────────────────────────────────────
        base = base.offset(offset).limit(limit)

        result = await session.execute(base)
        items = list(result.scalars().all())

        count_result = await session.execute(count_base)
        total = count_result.scalar() or 0

        return items, total

    @staticmethod
    async def get_relevant_memories(
        session: AsyncSession,
        query: str | None = None,
        limit: int = 10,
    ) -> list[MemoryItem]:
        """
        Retrieve the most relevant active memories.

        If *query* is provided, perform keyword ILIKE match.
        Otherwise return high-importance active memories.

        Always filters to status = 'active'.
        """
        stmt = select(MemoryItem).where(MemoryItem.status == "active")

        if query:
            pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    MemoryItem.summary.ilike(pattern),
                    MemoryItem.statement.ilike(pattern),
                )
            )

        stmt = stmt.order_by(
            MemoryItem.importance_score.desc().nullslast(),
            MemoryItem.salience_score.desc().nullslast(),
        ).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())
