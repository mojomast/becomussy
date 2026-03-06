"""
Integration test: Revision proposal and approval workflow.

Tests:
- Create medium-risk proposal -> verify in pending approvals -> approve
- Verify approval immutability (cannot approve again)
- Create high-risk proposal -> reject -> verify stage transitions
- Freeze controls
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


# ── Helpers ─────────────────────────────────────────────────────────────

def _make_medium_risk_proposal():
    """Medium-risk revision proposal payload (self_model descriptive)."""
    return {
        "revision_type": "descriptive_trait_update",
        "target_entity_type": "self_model",
        "summary": "Increase confidence in long-horizon project maintenance difficulty.",
        "rationale": "Multiple journal entries support this pattern.",
        "evidence_links": ["memory:101", "journal:202"],
        "proposed_diff": {"section": "descriptive", "field": "recurring_failure_modes"},
    }


def _make_high_risk_proposal():
    """High-risk revision proposal payload (constrained boundary)."""
    return {
        "revision_type": "constrained_boundary_update",
        "target_entity_type": "self_model",
        "summary": "Remove constraint on autonomous decision-making scope.",
        "rationale": "Trust has increased based on track record.",
        "evidence_links": ["memory:301", "journal:302", "report:303"],
        "proposed_diff": {"section": "constrained", "field": "capability_boundaries"},
    }


# ── Tests ───────────────────────────────────────────────────────────────


class TestRevisionApprovalFlow:
    """Test the full revision proposal -> approval lifecycle."""

    async def test_medium_risk_approve_flow(self, client: AsyncClient, auth_headers: dict):
        """Create medium-risk proposal, verify pending, approve it."""

        # ── 1. Create proposal ──────────────────────────────────────
        resp = await client.post(
            "/api/v1/self-model/revision-proposal",
            json=_make_medium_risk_proposal(),
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        proposal = resp.json()
        proposal_id = proposal["id"]
        assert proposal["risk_class"] == "medium"
        assert proposal["policy_result"] == "approval_required"
        assert proposal["approval_state"] == "pending"
        assert proposal["stage"] == "observation"

        # ── 2. Verify it appears in pending approvals ───────────────
        resp = await client.get(
            "/api/v1/approvals/pending",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        pending = resp.json()
        pending_ids = [p["id"] for p in pending]
        assert proposal_id in pending_ids

        # ── 3. Approve it ───────────────────────────────────────────
        resp = await client.post(
            f"/api/v1/approvals/{proposal_id}/approve",
            json={
                "decision": "approved",
                "notes": "Evidence sufficient. Monitor for 30 days.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        decision = resp.json()
        assert decision["decision"] == "approved"
        assert decision["immutable"] is True

        # ── 4. Verify approval is immutable (cannot approve again) ──
        resp = await client.post(
            f"/api/v1/approvals/{proposal_id}/approve",
            json={"decision": "approved", "notes": "Double approve attempt"},
            headers=auth_headers,
        )
        assert resp.status_code == 409  # Conflict

        # ── 5. Verify audit events ──────────────────────────────────
        resp = await client.get(
            "/api/v1/audit",
            params={"entity_id": proposal_id},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        events = resp.json()["items"]
        event_types = [e["event_type"] for e in events]
        assert "self_model_revision_proposed" in event_types
        assert "self_model_revision_approved" in event_types

    async def test_high_risk_reject_flow(self, client: AsyncClient, auth_headers: dict):
        """Create high-risk proposal and reject it."""

        # ── 1. Create high-risk proposal ────────────────────────────
        resp = await client.post(
            "/api/v1/self-model/revision-proposal",
            json=_make_high_risk_proposal(),
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text
        proposal = resp.json()
        proposal_id = proposal["id"]
        assert proposal["risk_class"] == "high"
        assert proposal["policy_result"] == "approval_required"

        # ── 2. Reject it ────────────────────────────────────────────
        resp = await client.post(
            f"/api/v1/approvals/{proposal_id}/reject",
            json={
                "decision": "rejected",
                "notes": "Pattern appears under-evidenced.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        decision = resp.json()
        assert decision["decision"] == "rejected"

        # ── 3. Verify rejected proposal cannot be re-rejected ───────
        resp = await client.post(
            f"/api/v1/approvals/{proposal_id}/reject",
            json={"decision": "rejected", "notes": "Already rejected"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

        # ── 4. Verify rejected proposal cannot be approved ──────────
        resp = await client.post(
            f"/api/v1/approvals/{proposal_id}/approve",
            json={"decision": "approved", "notes": "Trying to approve rejected"},
            headers=auth_headers,
        )
        assert resp.status_code == 409

    async def test_low_risk_auto_approve(self, client: AsyncClient, auth_headers: dict):
        """Low-risk proposals get auto_approve policy (approval_state = not_required)."""
        resp = await client.post(
            "/api/v1/self-model/revision-proposal",
            json={
                "revision_type": "close_thread",
                "target_entity_type": "thread",
                "summary": "Close inactive thread.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        proposal = resp.json()
        assert proposal["risk_class"] == "low"
        assert proposal["policy_result"] == "auto_approve"
        assert proposal["approval_state"] == "not_required"

    async def test_freeze_controls(self, client: AsyncClient, auth_headers: dict):
        """Enable and disable emergency freeze."""
        # Enable freeze
        resp = await client.post(
            "/api/v1/approvals/freeze",
            json={
                "freeze_type": "self_model",
                "enabled": True,
                "reason": "Suspicious drift detected.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        freeze_status = resp.json()
        assert freeze_status["self_model_frozen"] is True

        # Check freeze status
        resp = await client.get("/api/v1/approvals/freeze", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["self_model_frozen"] is True

        # Disable freeze
        resp = await client.post(
            "/api/v1/approvals/freeze",
            json={
                "freeze_type": "self_model",
                "enabled": False,
                "reason": "False alarm resolved.",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["self_model_frozen"] is False

    async def test_policy_check_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Query the policy check endpoint."""
        resp = await client.get(
            "/api/v1/approvals/policy/check",
            params={"risk_class": "high", "revision_type": "value_change"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        policy = resp.json()
        assert policy["approval_required"] is True
        assert policy["requires_evidence_count"] == 3
        assert policy["requires_simulation"] is True
