"""
Integration test: Memory link operations.

Tests contradict and link operations between memory items.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestMemoryLinks:
    """Test memory linking and contradiction operations."""

    async def test_contradict_memory(self, client: AsyncClient, auth_headers: dict):
        """Create a contradiction link between two memories."""

        # Create first memory
        resp1 = await client.post(
            "/api/v1/memory",
            json={
                "memory_type": "semantic",
                "summary": "Original belief: Use PostgreSQL for everything",
                "statement": "PostgreSQL is the best database for all use cases.",
                "importance_score": "70",
            },
            headers=auth_headers,
        )
        assert resp1.status_code == 201, resp1.text
        memory1 = resp1.json()
        memory1_id = memory1["id"]

        # Create second memory that contradicts the first
        resp2 = await client.post(
            "/api/v1/memory",
            json={
                "memory_type": "semantic",
                "summary": "Updated belief: Use right tool for the job",
                "statement": "Different databases have different strengths. PostgreSQL is not always the best choice.",
                "importance_score": "80",
            },
            headers=auth_headers,
        )
        assert resp2.status_code == 201, resp2.text
        memory2 = resp2.json()
        memory2_id = memory2["id"]

        # Create contradiction link
        resp = await client.post(
            f"/api/v1/memory/{memory1_id}/contradict",
            json={
                "contradicting_memory_id": memory2_id,
                "reason": "New evidence shows PostgreSQL isn't always optimal",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        link = resp.json()
        assert link["from_memory_id"] == memory2_id
        assert link["to_memory_id"] == memory1_id
        assert link["link_type"] == "contradicts"

        # Verify the link appears in the memory's incoming links
        resp = await client.get(
            f"/api/v1/memory/{memory1_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        fetched = resp.json()
        assert len(fetched["incoming_links"]) >= 1
        link_types = [l["link_type"] for l in fetched["incoming_links"]]
        assert "contradicts" in link_types

    async def test_contradict_nonexistent_memory(self, client: AsyncClient, auth_headers: dict):
        """Contradicting a non-existent memory returns 404."""
        fake_id = "00000000-0000-0000-0000-000000000001"
        resp = await client.post(
            f"/api/v1/memory/{fake_id}/contradict",
            json={
                "contradicting_memory_id": "00000000-0000-0000-0000-000000000002",
                "reason": "Test contradiction",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_reinforce_increases_salience(self, client: AsyncClient, auth_headers: dict):
        """Reinforcing a memory should increase its salience score."""

        # Create a memory
        resp = await client.post(
            "/api/v1/memory",
            json={
                "memory_type": "episodic",
                "summary": "Important learning about async patterns",
                "statement": "Discovered that async context managers work well for session management.",
                "importance_score": "75",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        memory = resp.json()
        memory_id = memory["id"]
        initial_salience = float(memory["salience_score"])

        # Reinforce multiple times
        for i in range(3):
            resp = await client.post(
                f"/api/v1/memory/{memory_id}/reinforce",
                json={
                    "reason": f"Reference {i+1}",
                    "source_ref": f"doc_{i+1}",
                },
                headers=auth_headers,
            )
            assert resp.status_code == 200

        # Check salience increased
        resp = await client.get(
            f"/api/v1/memory/{memory_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        updated = resp.json()
        final_salience = float(updated["salience_score"])
        assert final_salience > initial_salience
        # Should have increased by ~3 (one per reinforcement)
        assert final_salience >= initial_salience + 3

    async def test_reinforce_creates_self_link(self, client: AsyncClient, auth_headers: dict):
        """Reinforcing should create a 'supports' self-link."""

        # Create a memory
        resp = await client.post(
            "/api/v1/memory",
            json={
                "memory_type": "semantic",
                "summary": "Test memory for reinforcement",
                "statement": "This memory will be reinforced.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        memory = resp.json()
        memory_id = memory["id"]

        # Reinforce it
        resp = await client.post(
            f"/api/v1/memory/{memory_id}/reinforce",
            json={
                "reason": "Test reinforcement",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200

        # Check for self-link
        resp = await client.get(
            f"/api/v1/memory/{memory_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        fetched = resp.json()

        # Should have at least one outgoing link (the self-link)
        assert len(fetched["outgoing_links"]) >= 1
        self_links = [l for l in fetched["outgoing_links"] if l["to_memory_id"] == memory_id]
        assert len(self_links) >= 1
        assert self_links[0]["link_type"] == "supports"
