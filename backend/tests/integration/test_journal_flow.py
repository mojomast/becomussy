"""
Integration test: Journal entry lifecycle flow.

Tests the full journal API: create -> retrieve -> search -> update ->
summarize -> verify links.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestJournalFlow:
    """End-to-end journal lifecycle via the API."""

    async def test_full_journal_lifecycle(self, client: AsyncClient, auth_headers: dict):
        """Create, retrieve, search, update journal entry – verify all fields."""

        # ── 1. Create a journal entry ─────────────────────────────────
        create_payload = {
            "entry_type": "milestone",
            "title": "Night Shift Summary",
            "body_md": "## Accomplishments\n\n- Added thread management UI\n- Fixed MissingGreenlet bug\n- Wrote integration tests\n\n## Next Steps\n\n- Deploy to production\n- Monitor performance",
            "confidence_level": "high",
            "tags": ["night-shift", "feature", "testing"],
            "linked_memory_ids": [],
            "linked_project_ids": [],
            "linked_identity_themes": ["becomussy-integration"],
            "follow_up_candidates": [],
            "provenance": {"source": "hermes-night-shift"},
        }
        resp = await client.post(
            "/api/v1/journal",
            json=create_payload,
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        entry = resp.json()
        entry_id = entry["id"]
        assert entry["entry_type"] == "milestone"
        assert entry["title"] == create_payload["title"]
        assert entry["body_md"] == create_payload["body_md"]
        assert entry["tags"] == ["night-shift", "feature", "testing"]
        assert entry["confidence_level"] == "high"
        assert entry["linked_identity_themes"] == ["becomussy-integration"]

        # ── 2. Retrieve it ──────────────────────────────────────────
        resp = await client.get(
            f"/api/v1/journal/{entry_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        fetched = resp.json()
        assert fetched["id"] == entry_id
        assert fetched["title"] == create_payload["title"]
        assert "created_at" in fetched
        assert "updated_at" in fetched
        assert fetched["created_by"] == "test-steward"

        # ── 3. Search for it ────────────────────────────────────────
        resp = await client.get(
            "/api/v1/journal/search",
            params={"keyword": "thread management"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        search_results = resp.json()
        assert search_results["total"] >= 1
        found_ids = [item["id"] for item in search_results["items"]]
        assert entry_id in found_ids

        # ── 4. Update it ────────────────────────────────────────────
        resp = await client.patch(
            f"/api/v1/journal/{entry_id}",
            json={
                "title": "Night Shift Summary (Updated)",
                "tags": ["night-shift", "feature", "testing", "updated"],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["title"] == "Night Shift Summary (Updated)"
        assert "updated" in updated["tags"]
        assert updated["updated_by"] == "test-steward"

    async def test_journal_not_found(self, client: AsyncClient, auth_headers: dict):
        """Getting a non-existent journal entry returns 404."""
        resp = await client.get(
            "/api/v1/journal/00000000-0000-0000-0000-000000000002",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_search_with_entry_type_filter(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Create multiple entries and search by type."""
        # Create a milestone entry
        await client.post(
            "/api/v1/journal",
            json={
                "entry_type": "milestone",
                "title": "Milestone Test",
                "body_md": "Milestone content",
            },
            headers=auth_headers,
        )
        # Create a reflection entry
        await client.post(
            "/api/v1/journal",
            json={
                "entry_type": "reflection",
                "title": "Reflection Test",
                "body_md": "Reflection content",
            },
            headers=auth_headers,
        )

        # Search only milestone entries
        resp = await client.get(
            "/api/v1/journal/search",
            params={"entry_type": "milestone"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        results = resp.json()
        for item in results["items"]:
            assert item["entry_type"] == "milestone"

    async def test_search_with_date_filter(self, client: AsyncClient, auth_headers: dict):
        """Filter journal entries by date range."""
        from datetime import timezone
        now = datetime.now(timezone.utc)

        # Create an entry
        resp = await client.post(
            "/api/v1/journal",
            json={
                "entry_type": "milestone",
                "title": "Date Filter Test",
                "body_md": "Testing date filtering",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201

        # Search within a wide date range
        resp = await client.get(
            "/api/v1/journal/search",
            params={
                "date_from": (now - timedelta(days=1)).isoformat(),
                "date_to": (now + timedelta(days=1)).isoformat(),
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        results = resp.json()
        assert results["total"] >= 1

        # Search outside the date range (should not find the entry)
        resp = await client.get(
            "/api/v1/journal/search",
            params={
                "date_from": (now + timedelta(days=2)).isoformat(),
                "date_to": (now + timedelta(days=3)).isoformat(),
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        results = resp.json()
        # Entry was created today, so it shouldn't be in future range
        assert results["total"] == 0

    async def test_summarize_journal_entries(self, client: AsyncClient, auth_headers: dict):
        """Summarize journal entries within a date range."""
        from datetime import timezone
        now = datetime.now(timezone.utc)

        # Create a few entries
        for i in range(3):
            await client.post(
                "/api/v1/journal",
                json={
                    "entry_type": "milestone",
                    "title": f"Summary Test Entry {i}",
                    "body_md": f"Content for entry {i}",
                },
                headers=auth_headers,
            )

        # Request summary
        resp = await client.post(
            "/api/v1/journal/summarize",
            json={
                "range_start": (now - timedelta(days=1)).isoformat(),
                "range_end": (now + timedelta(days=1)).isoformat(),
                "summary_type": "daily",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        entries = resp.json()
        # Should return at least the entries we just created
        assert len(entries) >= 3
        titles = [e["title"] for e in entries]
        assert any("Summary Test Entry" in t for t in titles)

    async def test_create_with_linked_memory(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Create journal entry linked to a memory."""
        # First create a memory
        mem_resp = await client.post(
            "/api/v1/memory",
            json={
                "memory_type": "episodic",
                "summary": "Memory to link to journal",
            },
            headers=auth_headers,
        )
        assert mem_resp.status_code == 201
        memory_id = mem_resp.json()["id"]

        # Create journal entry with linked memory
        resp = await client.post(
            "/api/v1/journal",
            json={
                "entry_type": "reflection",
                "title": "Linked Memory Journal",
                "body_md": "This entry is linked to a memory",
                "linked_memory_ids": [memory_id],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        entry = resp.json()
        assert memory_id in entry["linked_memory_ids"]

    async def test_update_nonexistent_journal(self, client: AsyncClient, auth_headers: dict):
        """Updating a non-existent journal entry returns 404."""
        resp = await client.patch(
            "/api/v1/journal/00000000-0000-0000-0000-000000000003",
            json={"title": "This should fail"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_create_missing_required_fields(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Creating entry without required fields returns validation error."""
        # Missing entry_type and title
        resp = await client.post(
            "/api/v1/journal",
            json={"body_md": "Only body, no title or type"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_create_with_extra_fields_fails(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Creating entry with extra fields fails due to extra='forbid'."""
        resp = await client.post(
            "/api/v1/journal",
            json={
                "entry_type": "milestone",
                "title": "Test",
                "body_md": "Content",
                "extra_unexpected_field": "should fail",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 422

    async def test_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test pagination of journal search results."""
        # Create multiple entries
        for i in range(5):
            await client.post(
                "/api/v1/journal",
                json={
                    "entry_type": "milestone",
                    "title": f"Pagination Test {i}",
                    "body_md": f"Entry number {i}",
                },
                headers=auth_headers,
            )

        # Get first page
        resp = await client.get(
            "/api/v1/journal/search",
            params={"limit": 2, "offset": 0},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        page1 = resp.json()
        assert len(page1["items"]) == 2

        # Get second page
        resp = await client.get(
            "/api/v1/journal/search",
            params={"limit": 2, "offset": 2},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        page2 = resp.json()
        assert len(page2["items"]) == 2

        # Pages should have different items
        page1_ids = {item["id"] for item in page1["items"]}
        page2_ids = {item["id"] for item in page2["items"]}
        assert page1_ids.isdisjoint(page2_ids)
