"""
Integration test fixtures – requires a running PostgreSQL instance.

Provides:
- Database setup/teardown (session scope)
- Per-test transactional session with rollback
- httpx.AsyncClient bound to the FastAPI app
- Auth header fixtures

Note: The engine is created inside each fixture to ensure it uses
the correct event loop. This avoids the "Future attached to a different loop"
error with asyncpg and pytest-asyncio.
"""

from __future__ import annotations

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.base import Base, get_session
from app.main import app

# ── Test database URL ───────────────────────────────────────────────────
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://becoming:becoming@localhost:5433/becoming_test",
)


def _create_test_engine():
    """Create a test engine with NullPool for fresh connections."""
    return create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # No pooling - fresh connections each time
    )


# ── Create / drop tables for the whole test session ─────────────────────
# Use loop_scope="session" to avoid the "ScopeMismatch" error with session-scoped fixtures
@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def _setup_database():
    """Create all tables before integration tests, drop them after."""
    import app.models  # noqa: F401

    engine = _create_test_engine()

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ── Per-test transactional session (rolls back after each test) ─────────
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async session wrapped in a transaction that is rolled back
    after the test completes, ensuring test isolation.
    
    Creates a fresh engine for each test to avoid event loop binding issues.
    """
    engine = _create_test_engine()
    async with engine.connect() as conn:
        txn = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)

        try:
            yield session
        finally:
            await session.close()
            await txn.rollback()
    
    await engine.dispose()


# ── FastAPI test client with dependency override ────────────────────────
@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an httpx.AsyncClient that is wired to use the test session
    instead of the production session. This ensures all API calls go
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
