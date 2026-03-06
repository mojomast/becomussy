"""
Integration test: Memory lifecycle flow.

Tests the full memory API: create -> retrieve -> search -> update ->
reinforce -> verify audit trail.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestMemoryFlow:
    """End-to-end memory lifecycle via the API."""

    async def test_full_memory_lifecycle(self, client: AsyncClient, auth_headers: dict):
        """Create, retrieve, search, update, reinforce – verify audit events."""

        # ── 1. Create a memory item ─────────────────────────────────
        create_payload = {
            "memory_type": "episodic",
            "summary": "Discussed architecture for the becoming system.",
            "statement": "Agent and steward agreed on modular monolith approach.",
            "importance_score": "0.85",
            "confidence_level": "high",
            "metadata": {
                "participants": ["agent", "steward"],
                "linked_projects": ["becoming-mvp"],
            },
        }
        resp = await client.post(
            "/api/v1/memory",
            json=create_payload,
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        memory = resp.json()
        memory_id = memory["id"]
        assert memory["memory_type"] == "episodic"
        assert memory["summary"] == create_payload["summary"]
        assert memory["status"] == "active"

        # ── 2. Retrieve it ──────────────────────────────────────────
        resp = await client.get(
            f"/api/v1/memory/{memory_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        fetched = resp.json()
        assert fetched["id"] == memory_id
        assert fetched["statement"] == create_payload["statement"]

        # ── 3. Search for it ────────────────────────────────────────
        resp = await client.get(
            "/api/v1/memory/search",
            params={"q": "architecture"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        search_results = resp.json()
        assert search_results["total"] >= 1
        found_ids = [item["id"] for item in search_results["items"]]
        assert memory_id in found_ids

        # ── 4. Update it ────────────────────────────────────────────
        resp = await client.patch(
            f"/api/v1/memory/{memory_id}",
            json={"summary": "Updated: architecture discussion with next steps."},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        updated = resp.json()
        assert "Updated:" in updated["summary"]

        # ── 5. Reinforce it ─────────────────────────────────────────
        resp = await client.post(
            f"/api/v1/memory/{memory_id}/reinforce",
            json={
                "reason": "Referenced in weekly synthesis",
                "source_ref": "report_2026_w10",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        reinforced = resp.json()
        # salience_score should have increased
        assert float(reinforced["salience_score"]) > 0

        # ── 6. Verify audit events were created ─────────────────────
        resp = await client.get(
            "/api/v1/audit",
            params={"entity_id": memory_id},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        audit_data = resp.json()
        event_types = [e["event_type"] for e in audit_data["items"]]
        assert "memory_created" in event_types
        assert "memory_reinforced" in event_types

    async def test_memory_not_found(self, client: AsyncClient, auth_headers: dict):
        """Getting a non-existent memory returns 404."""
        resp = await client.get(
            "/api/v1/memory/00000000-0000-0000-0000-000000000001",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_search_with_type_filter(self, client: AsyncClient, auth_headers: dict):
        """Create multiple memories and search by type."""
        # Create episodic
        await client.post(
            "/api/v1/memory",
            json={"memory_type": "episodic", "summary": "Episodic test entry"},
            headers=auth_headers,
        )
        # Create semantic
        await client.post(
            "/api/v1/memory",
            json={"memory_type": "semantic", "summary": "Semantic test entry"},
            headers=auth_headers,
        )

        # Search only episodic
        resp = await client.get(
            "/api/v1/memory/search",
            params={"memory_type": "episodic", "q": "test entry"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        results = resp.json()
        for item in results["items"]:
            assert item["memory_type"] == "episodic"
