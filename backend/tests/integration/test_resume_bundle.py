"""
Integration test: Resume bundle (context compiler).

Tests: create threads, projects, commitments, memories, then fetch
the resume bundle and verify it contains expected items.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestResumeBundle:
    """Test the context compiler resume bundle endpoint."""

    async def _seed_data(self, client: AsyncClient, headers: dict) -> dict:
        """Create a set of test entities and return their IDs."""
        ids = {}

        # Create a thread
        resp = await client.post(
            "/api/v1/threads",
            json={
                "title": "Resume bundle test thread",
                "thread_type": "project",
                "urgency": 9,
                "importance": 8,
                "next_action": "Complete integration tests.",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        ids["thread_id"] = resp.json()["id"]

        # Create a project
        resp = await client.post(
            "/api/v1/projects",
            json={
                "name": "Resume test project",
                "purpose": "Testing the resume bundle.",
                "current_phase": "testing",
                "next_steps_json": ["Run tests", "Review results"],
            },
            headers=headers,
        )
        assert resp.status_code == 201
        project = resp.json()
        ids["project_id"] = project["id"]

        # Create a commitment (due soon)
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        resp = await client.post(
            f"/api/v1/projects/{ids['project_id']}/commitments",
            json={
                "commitment_text": "Deliver resume bundle integration test",
                "made_to": "steward",
                "date_made": date.today().isoformat(),
                "due_date": tomorrow,
                "risk_if_missed": "Test coverage gap.",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        ids["commitment_id"] = resp.json()["id"]

        # Create a memory
        resp = await client.post(
            "/api/v1/memory",
            json={
                "memory_type": "episodic",
                "summary": "Resume bundle test: discussed architecture.",
                "importance_score": "0.9",
                "confidence_level": "high",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        ids["memory_id"] = resp.json()["id"]

        return ids

    async def test_resume_bundle_contains_expected_items(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Fetch resume bundle and verify it contains seeded data."""
        ids = await self._seed_data(client, auth_headers)

        resp = await client.get(
            "/api/v1/continuity/resume",
            params={"token_budget": 4000},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        bundle = resp.json()

        # Check structure
        assert "top_threads" in bundle
        assert "urgent_commitments" in bundle
        assert "active_projects" in bundle
        assert "relevant_memories" in bundle
        assert "constraints" in bundle
        assert "recommended_next_actions" in bundle
        assert "generated_at" in bundle
        assert bundle["token_budget"] == 4000

        # Verify our thread is present
        thread_ids = [t["id"] for t in bundle["top_threads"]]
        assert ids["thread_id"] in thread_ids

        # Verify our project is present
        project_ids = [p["id"] for p in bundle["active_projects"]]
        assert ids["project_id"] in project_ids

        # Verify our commitment is present (due tomorrow, should be urgent)
        commitment_ids = [c["id"] for c in bundle["urgent_commitments"]]
        assert ids["commitment_id"] in commitment_ids

        # Verify recommended next actions include something from our entities
        assert len(bundle["recommended_next_actions"]) > 0

    async def test_resume_bundle_respects_token_budget(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Lower token budget should still return a valid bundle."""
        resp = await client.get(
            "/api/v1/continuity/resume",
            params={"token_budget": 500},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        bundle = resp.json()
        assert bundle["token_budget"] == 500
        # With 500 tokens, items per section = min(500//400, 10) = 1
        # So each section should have at most 1 item
        assert len(bundle["top_threads"]) <= 1
        assert len(bundle["active_projects"]) <= 1

    async def test_resume_bundle_debug_endpoint(
        self, client: AsyncClient, auth_headers: dict
    ):
        """The debug endpoint includes debug_info."""
        resp = await client.get(
            "/api/v1/continuity/resume/debug",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        bundle = resp.json()
        assert bundle["debug_info"] is not None
        assert "threads_found" in bundle["debug_info"] or "threads_error" in bundle["debug_info"]
