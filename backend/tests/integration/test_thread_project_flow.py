"""
Integration test: Thread & Project lifecycle flow.

Tests: create thread, create project, create commitment, update thread,
list threads/projects, verify audit trail.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestThreadProjectFlow:
    """End-to-end thread and project lifecycle via the API."""

    async def test_thread_crud_and_listing(self, client: AsyncClient, auth_headers: dict):
        """Create a thread, update it, list threads."""

        # ── 1. Create a thread ──────────────────────────────────────
        resp = await client.post(
            "/api/v1/threads",
            json={
                "title": "Architecture design decisions",
                "description": "Track key architectural choices for the system.",
                "thread_type": "project",
                "urgency": 8,
                "importance": 9,
                "next_action": "Review module boundaries.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        thread = resp.json()
        thread_id = thread["id"]
        assert thread["title"] == "Architecture design decisions"
        assert thread["status"] == "active"
        assert thread["urgency"] == 8

        # ── 2. Update thread status ─────────────────────────────────
        resp = await client.patch(
            f"/api/v1/threads/{thread_id}",
            json={
                "status": "archived",
                "next_action": "Completed review. Archive.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["status"] == "archived"

        # ── 3. List threads ─────────────────────────────────────────
        resp = await client.get(
            "/api/v1/threads",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

        # ── 4. Verify audit trail ───────────────────────────────────
        resp = await client.get(
            "/api/v1/audit",
            params={"entity_id": thread_id},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        events = resp.json()["items"]
        event_types = [e["event_type"] for e in events]
        assert "thread_created" in event_types
        assert "thread_updated" in event_types

    async def test_project_with_commitments(self, client: AsyncClient, auth_headers: dict):
        """Create a project, add commitments, list them."""

        # ── 1. Create a project ─────────────────────────────────────
        resp = await client.post(
            "/api/v1/projects",
            json={
                "name": "becomussy MVP",
                "purpose": "Build the initial governed continuity system.",
                "current_phase": "implementation",
                "linked_themes": ["continuity", "governance"],
                "next_steps_json": [{"step": "Finish backend", "priority": "high"}],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        project = resp.json()
        project_id = project["id"]
        assert project["name"] == "becomussy MVP"
        assert project["status"] == "active"

        # ── 2. Create a commitment ──────────────────────────────────
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        resp = await client.post(
            f"/api/v1/projects/{project_id}/commitments",
            json={
                "commitment_text": "Complete memory service implementation",
                "made_to": "steward",
                "date_made": date.today().isoformat(),
                "due_date": tomorrow,
                "risk_if_missed": "Delays the entire MVP timeline.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        commitment = resp.json()
        assert commitment["project_id"] == project_id
        assert commitment["status"] == "active"

        # ── 3. List project commitments ─────────────────────────────
        resp = await client.get(
            f"/api/v1/projects/{project_id}/commitments",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert any(
            c["commitment_text"] == "Complete memory service implementation"
            for c in data["items"]
        )

        # ── 4. List all projects ────────────────────────────────────
        resp = await client.get("/api/v1/projects", headers=auth_headers)
        assert resp.status_code == 200
        projects_data = resp.json()
        assert projects_data["total"] >= 1

        # ── 5. Verify audit trail ───────────────────────────────────
        resp = await client.get(
            "/api/v1/audit",
            params={"entity_type": "project"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        events = resp.json()["items"]
        assert any(e["event_type"] == "project_created" for e in events)

    async def test_commitment_top_level_crud(self, client: AsyncClient, auth_headers: dict):
        """Create and list commitments at the top-level endpoint."""
        resp = await client.post(
            "/api/v1/commitments",
            json={
                "commitment_text": "Write integration tests",
                "date_made": date.today().isoformat(),
                "risk_if_missed": "Reduced confidence in system quality.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        commitment = resp.json()
        commitment_id = commitment["id"]

        # List all
        resp = await client.get("/api/v1/commitments", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

        # Get specific
        resp = await client.get(
            f"/api/v1/commitments/{commitment_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["commitment_text"] == "Write integration tests"
