"""
Integration test fixtures – requires a running PostgreSQL instance.

Provides:
- Database setup/teardown (session scope)
- Per-test transactional session with rollback
- httpx.AsyncClient bound to the FastAPI app
- Auth header fixtures
"""

from __future__ import annotations

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base, get_session
from app.main import app

# ── Test database URL ───────────────────────────────────────────────────
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://becoming:becoming@localhost:5432/becoming_test",
)

# ── Engine & session factory scoped to the test session ─────────────────
_test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_pre_ping=True)
_test_session_factory = async_sessionmaker(
    _test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Create / drop tables for the whole test session ─────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def _setup_database():
    """Create all tables before integration tests, drop them after."""
    # Import all models so metadata is populated
    import app.models  # noqa: F401

    async with _test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await _test_engine.dispose()


# ── Per-test transactional session (rolls back after each test) ─────────
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async session wrapped in a transaction that is rolled back
    after the test completes, ensuring test isolation.
    """
    async with _test_engine.connect() as conn:
        txn = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)

        try:
            yield session
        finally:
            await session.close()
            await txn.rollback()


# ── FastAPI test client with dependency override ────────────────────────
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an httpx.AsyncClient that is wired to use the test session
    instead of the production session.  This ensures all API calls go
    through the same transaction that gets rolled back.
    """

    async def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ── Convenience headers fixture ─────────────────────────────────────────
@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Default auth headers for the steward role."""
    return {
        "X-User-Id": "test-steward",
        "X-User-Role": "steward",
    }


@pytest.fixture
def agent_headers() -> dict[str, str]:
    """Auth headers for the agent_runtime role."""
    return {
        "X-User-Id": "test-agent",
        "X-User-Role": "agent_runtime",
    }
