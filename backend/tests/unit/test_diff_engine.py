"""
Unit tests for the self-model diff engine.

Tests compare two SelfModelVersion section snapshots and verify the resulting
diff items are correct.
"""

from __future__ import annotations

import pytest

from app.schemas.self_model import SelfModelDiffItem
from app.services.self_model.diff_engine import compute_full_diff, diff_sections


# ── Helpers ─────────────────────────────────────────────────────────────

def _make_section(**overrides) -> dict:
    """Create a section dict with empty defaults, overridden by kwargs."""
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


def _empty_version():
    """All four sections empty."""
    return {
        "descriptive": _make_section(),
        "aspirational": _make_section(),
        "constrained": _make_section(),
        "relational": _make_section(),
    }


# ── Tests: diff_sections ───────────────────────────────────────────────


class TestDiffSections:
    """Test the per-section diff function."""

    def test_identical_sections_produce_no_diffs(self):
        old = _make_section(stable_traits=["curious", "precise"])
        new = _make_section(stable_traits=["curious", "precise"])
        result = diff_sections("descriptive", old, new)
        assert result == []

    def test_added_items_detected(self):
        old = _make_section(stable_traits=["curious"])
        new = _make_section(stable_traits=["curious", "persistent"])
        result = diff_sections("descriptive", old, new)
        assert len(result) == 1
        assert result[0].category == "added_theme"
        assert result[0].new_value == "persistent"
        assert result[0].prior_value is None
        assert result[0].section == "descriptive"

    def test_removed_items_detected(self):
        old = _make_section(current_aims=["build MVP", "learn Rust"])
        new = _make_section(current_aims=["build MVP"])
        result = diff_sections("aspirational", old, new)
        assert len(result) == 1
        assert result[0].category == "removed_theme"
        assert result[0].prior_value == "learn Rust"
        assert result[0].new_value is None

    def test_mixed_adds_and_removes(self):
        old = _make_section(
            key_tensions=["speed vs quality"],
            capability_boundaries=["cannot do math"],
        )
        new = _make_section(
            key_tensions=["speed vs quality", "autonomy vs safety"],
            capability_boundaries=[],
        )
        result = diff_sections("constrained", old, new)
        added = [d for d in result if d.category == "added_theme"]
        removed = [d for d in result if d.category == "removed_theme"]
        assert len(added) == 1
        assert added[0].new_value == "autonomy vs safety"
        assert len(removed) == 1
        assert removed[0].prior_value == "cannot do math"

    def test_both_none_produces_no_diffs(self):
        result = diff_sections("relational", None, None)
        assert result == []

    def test_old_none_new_populated(self):
        new = _make_section(identity_narratives=["growing"])
        result = diff_sections("descriptive", None, new)
        assert len(result) == 1
        assert result[0].category == "added_theme"
        assert result[0].new_value == "growing"

    def test_old_populated_new_none(self):
        old = _make_section(identity_narratives=["growing"])
        result = diff_sections("descriptive", old, None)
        assert len(result) == 1
        assert result[0].category == "removed_theme"
        assert result[0].prior_value == "growing"


# ── Tests: compute_full_diff ───────────────────────────────────────────


class TestComputeFullDiff:
    """Test the full cross-section diff computation."""

    def test_identical_versions_no_diffs(self):
        version = _empty_version()
        result = compute_full_diff(version, version)
        assert result == []

    def test_changes_across_multiple_sections(self):
        old = _empty_version()
        old["descriptive"]["stable_traits"] = ["curious"]
        old["constrained"]["capability_boundaries"] = ["no math"]

        new = _empty_version()
        new["descriptive"]["stable_traits"] = ["curious", "creative"]
        new["aspirational"]["current_aims"] = ["ship MVP"]
        # constrained boundary removed (now empty)

        result = compute_full_diff(old, new)
        assert len(result) == 3

        categories = {d.category for d in result}
        assert "added_theme" in categories
        assert "removed_theme" in categories

        sections = {d.section for d in result}
        assert "descriptive" in sections
        assert "aspirational" in sections
        assert "constrained" in sections

    def test_all_empty_sections(self):
        result = compute_full_diff(_empty_version(), _empty_version())
        assert result == []

    def test_diffs_include_correct_evidence_links(self):
        """Evidence links default to empty list in MVP diff engine."""
        old = _empty_version()
        new = _empty_version()
        new["relational"]["value_hypotheses"] = ["trust is earned"]
        result = compute_full_diff(old, new)
        assert len(result) == 1
        assert result[0].evidence_links == []
