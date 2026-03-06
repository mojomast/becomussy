"""
Unit tests for revision risk classification logic.

Tests the _classify_risk and _determine_policy helper functions
from the revisions service.
"""

from __future__ import annotations

import pytest

from app.services.revisions import _classify_risk, _determine_policy


# ── Risk classification tests ──────────────────────────────────────────


class TestClassifyRisk:
    """Test risk classification based on revision_type and target_entity_type."""

    def test_constrained_target_is_high_risk(self):
        """Changes to constrained self-model boundaries are high risk."""
        assert _classify_risk("constrained_boundary_update", "self_model") == "high"
        assert _classify_risk("change constraint", "self_model") == "high"

    def test_value_hypothesis_is_high_risk(self):
        """Value-related changes to self-model are high risk."""
        assert _classify_risk("value_hypothesis_update", "self_model") == "high"
        assert _classify_risk("alter_values", "self_model") == "high"

    def test_boundary_keyword_is_high_risk(self):
        """The word 'boundary' in revision type triggers high risk."""
        assert _classify_risk("capability_boundary_change", "self_model") == "high"

    def test_descriptive_target_is_medium_risk(self):
        """Descriptive self-model changes are medium risk."""
        assert _classify_risk("descriptive_trait_update", "self_model") == "medium"
        assert _classify_risk("trait_adjustment", "self_model") == "medium"
        assert _classify_risk("description_change", "self_model") == "medium"

    def test_tendency_keyword_is_medium(self):
        """Tendency-related descriptive changes are medium risk."""
        assert _classify_risk("tendency_update", "self_model") == "medium"

    def test_thread_target_is_low_risk(self):
        """Thread-level changes are always low risk."""
        assert _classify_risk("close_thread", "thread") == "low"
        assert _classify_risk("constrained_change", "thread") == "low"

    def test_project_target_is_low_risk(self):
        """Project-level changes are always low risk."""
        assert _classify_risk("reprioritize", "project") == "low"
        assert _classify_risk("value_update", "project") == "low"

    def test_unknown_target_defaults_to_medium(self):
        """Unknown target types default to medium risk."""
        assert _classify_risk("random_change", "something_else") == "medium"

    def test_self_model_without_keywords_defaults_to_medium(self):
        """Self-model changes without matching keywords default to medium."""
        assert _classify_risk("general_update", "self_model") == "medium"

    def test_case_insensitive(self):
        """Classification is case-insensitive."""
        assert _classify_risk("CONSTRAINED_update", "SELF_MODEL") == "high"
        assert _classify_risk("Descriptive_Change", "Self_Model") == "medium"
        assert _classify_risk("anything", "Thread") == "low"
        assert _classify_risk("anything", "PROJECT") == "low"


# ── Policy determination tests ─────────────────────────────────────────


class TestDeterminePolicy:
    """Test policy_result determination from risk class."""

    def test_low_risk_auto_approve(self):
        assert _determine_policy("low") == "auto_approve"

    def test_medium_risk_approval_required(self):
        assert _determine_policy("medium") == "approval_required"

    def test_high_risk_approval_required(self):
        assert _determine_policy("high") == "approval_required"

    def test_unknown_risk_defaults_to_approval_required(self):
        """Any non-'low' value results in approval_required."""
        assert _determine_policy("extreme") == "approval_required"
        assert _determine_policy("") == "approval_required"
