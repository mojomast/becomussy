"""
Integration test: Self-model versioning and diffing flow.

Tests: create versions, compute diff, check history.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


# ── Helpers ─────────────────────────────────────────────────────────────

def _make_section(**overrides) -> dict:
    """Create a section payload with empty defaults."""
    base = {
        "stable_traits": [],
        "current_aims": [],
        "recurring_strengths": [],
        "recurring_failure_modes": [],
        "attention_patterns": [],
        "memory_tendencies": [],
        "preferred_working_styles": [],
        "identity_narratives": [],
        "key_tensions": [],
        "value_hypotheses": [],
        "capability_boundaries": [],
        "open_development_questions": [],
    }
    base.update(overrides)
    return base


def _make_version_payload(
    authoring_process: str = "manual",
    descriptive: dict | None = None,
    aspirational: dict | None = None,
    constrained: dict | None = None,
    relational: dict | None = None,
) -> dict:
    return {
        "authoring_process": authoring_process,
        "confidence_level": "medium",
        "descriptive_json": descriptive or _make_section(),
        "aspirational_json": aspirational or _make_section(),
        "constrained_json": constrained or _make_section(),
        "relational_json": relational or _make_section(),
        "evidence_links": [],
    }


# ── Tests ───────────────────────────────────────────────────────────────


class TestSelfModelFlow:
    """Test self-model version creation, diffing, and history."""

    async def test_create_and_retrieve_version(self, client: AsyncClient, auth_headers: dict):
        """Create a self-model version and retrieve it."""
        payload = _make_version_payload(
            descriptive=_make_section(
                stable_traits=["curious", "methodical"],
                recurring_strengths=["deep analysis"],
            ),
        )
        resp = await client.post(
            "/api/v1/self-model/version",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        version = resp.json()
        version_id = version["id"]
        assert version["version_number"] >= 1
        assert version["approval_state"] == "approved"

        # Retrieve by ID
        resp = await client.get(
            f"/api/v1/self-model/version/{version_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        fetched = resp.json()
        assert fetched["id"] == version_id
        assert "curious" in fetched["descriptive_json"]["stable_traits"]

    async def test_diff_between_two_versions(self, client: AsyncClient, auth_headers: dict):
        """Create two versions with differences and compute their diff."""

        # Version A
        payload_a = _make_version_payload(
            authoring_process="manual_v1",
            descriptive=_make_section(
                stable_traits=["curious", "methodical"],
                recurring_strengths=["deep analysis"],
            ),
            constrained=_make_section(
                capability_boundaries=["cannot do math"],
            ),
        )
        resp = await client.post(
            "/api/v1/self-model/version",
            json=payload_a,
            headers=auth_headers,
        )
        assert resp.status_code == 201
        version_a = resp.json()

        # Version B (some changes)
        payload_b = _make_version_payload(
            authoring_process="manual_v2",
            descriptive=_make_section(
                stable_traits=["curious", "creative"],  # removed "methodical", added "creative"
                recurring_strengths=["deep analysis", "pattern recognition"],
            ),
            constrained=_make_section(
                capability_boundaries=[],  # removed the boundary
            ),
        )
        resp = await client.post(
            "/api/v1/self-model/version",
            json=payload_b,
            headers=auth_headers,
        )
        assert resp.status_code == 201
        version_b = resp.json()

        # Compute diff
        resp = await client.post(
            "/api/v1/self-model/diff",
            json={
                "from_version_id": version_a["id"],
                "to_version_id": version_b["id"],
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        diff = resp.json()
        assert diff["from_version"] == version_a["version_number"]
        assert diff["to_version"] == version_b["version_number"]
        assert len(diff["diffs"]) > 0

        # Verify diff categories
        categories = {d["category"] for d in diff["diffs"]}
        assert "added_theme" in categories or "removed_theme" in categories

        # Check specific changes
        added = [d for d in diff["diffs"] if d["category"] == "added_theme"]
        removed = [d for d in diff["diffs"] if d["category"] == "removed_theme"]
        added_values = [d["new_value"] for d in added]
        removed_values = [d["prior_value"] for d in removed]

        assert "creative" in added_values
        assert "methodical" in removed_values

    async def test_version_history(self, client: AsyncClient, auth_headers: dict):
        """Create multiple versions and check the history endpoint."""
        # Create at least one version
        payload = _make_version_payload(authoring_process="history_test")
        resp = await client.post(
            "/api/v1/self-model/version",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code == 201

        # Fetch history
        resp = await client.get(
            "/api/v1/self-model/history",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) >= 1
        # History should be ordered by version_number descending
        if len(history) >= 2:
            assert history[0]["version_number"] > history[1]["version_number"]

    async def test_get_current_version(self, client: AsyncClient, auth_headers: dict):
        """The /current endpoint returns the latest approved version."""
        # Create a version so at least one exists
        payload = _make_version_payload(authoring_process="current_test")
        resp = await client.post(
            "/api/v1/self-model/version",
            json=payload,
            headers=auth_headers,
        )
        assert resp.status_code == 201
        created = resp.json()

        resp = await client.get(
            "/api/v1/self-model/current",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        current = resp.json()
        # The current version should be the one we just created (or newer)
        assert current["version_number"] >= created["version_number"]
