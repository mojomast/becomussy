"""
Unit tests for the governance policy check.

Tests GovernanceService.check_policy() which evaluates policy rules
based on risk class and revision type.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.services.governance import GovernanceService


class TestCheckPolicy:
    """Test the governance policy check logic."""

    def test_low_risk_auto_approve(self):
        """Low risk -> auto_approve, 0 evidence, no simulation."""
        result = GovernanceService.check_policy("low", "close_thread")
        assert result["approval_required"] is False
        assert result["requires_evidence_count"] == 0
        assert result["requires_simulation"] is False
        assert result["policy"] == "auto_approve"
        assert result["risk_class"] == "low"
        assert result["revision_type"] == "close_thread"

    def test_medium_risk_approval_required(self):
        """Medium risk -> approval_required, 2 evidence items, no simulation."""
        result = GovernanceService.check_policy("medium", "trait_update")
        assert result["approval_required"] is True
        assert result["requires_evidence_count"] == 2
        assert result["requires_simulation"] is False
        assert result["policy"] == "approval_required"

    def test_high_risk_full_requirements(self):
        """High risk -> approval_required, 3 evidence items, simulation required."""
        result = GovernanceService.check_policy("high", "value_change")
        assert result["approval_required"] is True
        assert result["requires_evidence_count"] == 3
        assert result["requires_simulation"] is True
        assert result["policy"] == "approval_required"

    def test_invalid_risk_class_raises_http_exception(self):
        """Unknown risk class should raise an HTTPException (400)."""
        with pytest.raises(HTTPException) as exc_info:
            GovernanceService.check_policy("extreme", "anything")
        assert exc_info.value.status_code == 400
        assert "Unknown risk_class" in exc_info.value.detail

    def test_policy_preserves_revision_type_in_result(self):
        """The result dict should include the original revision_type."""
        result = GovernanceService.check_policy("low", "add_journal")
        assert result["revision_type"] == "add_journal"

    def test_policy_preserves_risk_class_in_result(self):
        """The result dict should include the original risk_class."""
        result = GovernanceService.check_policy("medium", "update_habit")
        assert result["risk_class"] == "medium"
