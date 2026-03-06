"""
becomussy – top-level pytest configuration.

Provides common non-DB fixtures. Database fixtures are in
tests/integration/conftest.py so unit tests can run without PostgreSQL.
"""

from __future__ import annotations

import asyncio

import pytest


# ── Event loop fixture (session scope) ──────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
