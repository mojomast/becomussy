"""
becomussy – top-level pytest configuration.

Provides common non-DB fixtures. Database fixtures are in
tests/integration/conftest.py so unit tests can run without PostgreSQL.

Note: The event_loop fixture is no longer needed with pytest-asyncio 0.23+.
The asyncio_default_fixture_loop_scope is configured in pyproject.toml.
"""

from __future__ import annotations

import pytest
