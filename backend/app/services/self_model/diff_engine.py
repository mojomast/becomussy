"""
becomussy – Self-Model diff engine.

Compares two SelfModelVersion records section by section and produces a
structured list of SelfModelDiffItem objects describing what changed.
"""

from __future__ import annotations

from typing import Any

from app.schemas.self_model import SelfModelDiffItem, SelfModelSectionSchema


# Fields within each section schema that we diff
_SECTION_FIELDS = [
    "stable_traits",
    "current_aims",
    "recurring_strengths",
    "recurring_failure_modes",
    "attention_patterns",
    "memory_tendencies",
    "preferred_working_styles",
    "identity_narratives",
    "key_tensions",
    "value_hypotheses",
    "capability_boundaries",
    "open_development_questions",
]


def _parse_section(raw: dict[str, Any] | None) -> SelfModelSectionSchema:
    """Parse a raw JSON dict into a SelfModelSectionSchema, defaulting if None."""
    if raw is None:
        return SelfModelSectionSchema()
    return SelfModelSectionSchema.model_validate(raw)


def diff_sections(
    section_name: str,
    old_raw: dict[str, Any] | None,
    new_raw: dict[str, Any] | None,
) -> list[SelfModelDiffItem]:
    """Compare two section dicts and return a list of diff items.

    For MVP, focuses on added/removed entries. Items present in both
    versions are treated as unchanged.
    """
    old_section = _parse_section(old_raw)
    new_section = _parse_section(new_raw)
    diffs: list[SelfModelDiffItem] = []

    for field_name in _SECTION_FIELDS:
        old_items: list[str] = getattr(old_section, field_name, [])
        new_items: list[str] = getattr(new_section, field_name, [])

        old_set = set(old_items)
        new_set = set(new_items)

        # Items added in the new version
        for item in sorted(new_set - old_set):
            diffs.append(
                SelfModelDiffItem(
                    category="added_theme",
                    section=section_name,
                    item=field_name,
                    prior_value=None,
                    new_value=item,
                    evidence_links=[],
                )
            )

        # Items removed from the old version
        for item in sorted(old_set - new_set):
            diffs.append(
                SelfModelDiffItem(
                    category="removed_theme",
                    section=section_name,
                    item=field_name,
                    prior_value=item,
                    new_value=None,
                    evidence_links=[],
                )
            )

    return diffs


def compute_full_diff(
    old_version_data: dict[str, dict[str, Any] | None],
    new_version_data: dict[str, dict[str, Any] | None],
) -> list[SelfModelDiffItem]:
    """Compute the complete diff across all four self-model sections.

    Parameters
    ----------
    old_version_data:
        Mapping of section name -> JSON dict for the older version.
        Expected keys: descriptive, aspirational, constrained, relational.
    new_version_data:
        Same structure for the newer version.

    Returns
    -------
    A flat list of SelfModelDiffItem describing every change.
    """
    section_names = ["descriptive", "aspirational", "constrained", "relational"]
    all_diffs: list[SelfModelDiffItem] = []

    for section_name in section_names:
        old_raw = old_version_data.get(section_name)
        new_raw = new_version_data.get(section_name)
        all_diffs.extend(diff_sections(section_name, old_raw, new_raw))

    return all_diffs
