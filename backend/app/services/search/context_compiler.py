"""
becomussy – Context Compiler.

Assembles a ResumeBundle by pulling data from all domain tables
to give the agent runtime a full continuity snapshot.

See spec §6 for the resume-bundle compilation algorithm.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import MemoryItem
from app.models.project import Commitment, Project
from app.models.self_model import SelfModelVersion
from app.models.thread import Thread
from app.schemas.continuity import (
    CommitmentSummary,
    IdentityChangeSummary,
    MemorySummary,
    ProjectSummary,
    ResumeBundle,
    ThreadSummary,
)
from app.services.search import SearchService

logger = logging.getLogger(__name__)


def _items_per_section(token_budget: int) -> int:
    """
    Rough heuristic: each item ~400 tokens.  Cap at 10 items per section.
    """
    return min(token_budget // 400, 10)


class ContextCompiler:
    """Compiles a ResumeBundle from the current system state."""

    @staticmethod
    async def compile_resume_bundle(
        session: AsyncSession,
        query: str | None = None,
        token_budget: int = 4000,
    ) -> ResumeBundle:
        """
        Assemble the resume bundle.

        Each section is fetched independently; if any section fails the
        compiler logs the error and continues with an empty list for that
        section.  This ensures the bundle is always returned.
        """
        max_items = _items_per_section(token_budget)
        now = datetime.now(timezone.utc)
        debug: dict[str, Any] = {}

        # ── 1. Active threads by urgency + importance ───────────────
        top_threads: list[ThreadSummary] = []
        try:
            stmt = (
                select(Thread)
                .where(Thread.status == "active")
                .order_by(
                    Thread.urgency.desc().nullslast(),
                    Thread.importance.desc().nullslast(),
                )
                .limit(max_items)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            top_threads = [
                ThreadSummary(
                    id=t.id,
                    title=t.title,
                    thread_type=t.thread_type,
                    status=t.status,
                    urgency=t.urgency,
                    importance=t.importance,
                    next_action=t.next_action,
                    blocker=t.blocker,
                    updated_at=t.updated_at,
                )
                for t in rows
            ]
            debug["threads_found"] = len(top_threads)
        except Exception:
            logger.exception("Failed to fetch threads for resume bundle")
            debug["threads_error"] = True

        # ── 2. Urgent commitments (due within 7 days or overdue) ────
        urgent_commitments: list[CommitmentSummary] = []
        try:
            seven_days_ahead = now + timedelta(days=7)
            stmt = (
                select(Commitment, Project.name.label("project_name"))
                .outerjoin(Project, Commitment.project_id == Project.id)
                .where(
                    Commitment.status == "active",
                    Commitment.due_date != None,  # noqa: E711 — SQLAlchemy requires != None
                    Commitment.due_date <= seven_days_ahead,
                )
                .order_by(Commitment.due_date.asc().nullslast())
                .limit(max_items)
            )
            result = await session.execute(stmt)
            for row in result.all():
                commitment = row[0]
                project_name = row[1]
                urgent_commitments.append(
                    CommitmentSummary(
                        id=commitment.id,
                        commitment_text=commitment.commitment_text,
                        made_to=commitment.made_to,
                        due_date=commitment.due_date,
                        status=commitment.status,
                        risk_if_missed=commitment.risk_if_missed,
                        project_name=project_name,
                    )
                )
            debug["commitments_found"] = len(urgent_commitments)
        except Exception:
            logger.exception("Failed to fetch commitments for resume bundle")
            debug["commitments_error"] = True

        # ── 3. Active projects with next steps ──────────────────────
        active_projects: list[ProjectSummary] = []
        try:
            stmt = (
                select(Project)
                .where(Project.status == "active")
                .order_by(Project.updated_at.desc())
                .limit(max_items)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            for p in rows:
                # next_steps_json may be a JSON list of strings or None
                next_steps = _parse_json_list(p.next_steps_json)
                active_projects.append(
                    ProjectSummary(
                        id=p.id,
                        name=p.name,
                        purpose=p.purpose,
                        current_phase=p.current_phase,
                        status=p.status,
                        next_steps=next_steps,
                    )
                )
            debug["projects_found"] = len(active_projects)
        except Exception:
            logger.exception("Failed to fetch projects for resume bundle")
            debug["projects_error"] = True

        # ── 4. Recent identity changes ──────────────────────────────
        recent_identity_changes: list[IdentityChangeSummary] = []
        try:
            stmt = (
                select(SelfModelVersion)
                .order_by(SelfModelVersion.version_number.desc())
                .limit(3)
            )
            result = await session.execute(stmt)
            versions = result.scalars().all()
            for v in versions:
                diff_summary = _extract_diff_summary(v.diff_from_prior_json)
                recent_identity_changes.append(
                    IdentityChangeSummary(
                        version_number=v.version_number,
                        timestamp=v.timestamp,
                        diff_summary=diff_summary,
                    )
                )
            debug["identity_versions_found"] = len(recent_identity_changes)
        except Exception:
            logger.exception("Failed to fetch identity changes for resume bundle")
            debug["identity_error"] = True

        # ── 5. Relevant memories ────────────────────────────────────
        relevant_memories: list[MemorySummary] = []
        try:
            if query:
                memories = await SearchService.get_relevant_memories(
                    session, query=query, limit=max_items
                )
            else:
                # Recent high-importance memories from the last 7 days
                seven_days_ago = now - timedelta(days=7)
                stmt = (
                    select(MemoryItem)
                    .where(
                        MemoryItem.status == "active",
                        MemoryItem.importance_score > 0.5,
                        MemoryItem.created_at >= seven_days_ago,
                    )
                    .order_by(
                        MemoryItem.importance_score.desc().nullslast(),
                        MemoryItem.created_at.desc(),
                    )
                    .limit(max_items)
                )
                result = await session.execute(stmt)
                memories = list(result.scalars().all())

            relevant_memories = [
                MemorySummary(
                    id=m.id,
                    memory_type=m.memory_type,
                    summary=m.summary,
                    importance_score=m.importance_score,
                    salience_score=m.salience_score,
                    timestamp=m.timestamp,
                )
                for m in memories
            ]
            debug["memories_found"] = len(relevant_memories)
        except Exception:
            logger.exception("Failed to fetch memories for resume bundle")
            debug["memories_error"] = True

        # ── 6. Extract constraints from latest self-model ───────────
        constraints: list[str] = []
        try:
            stmt = (
                select(SelfModelVersion)
                .order_by(SelfModelVersion.version_number.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            latest_version = result.scalar_one_or_none()
            if latest_version and latest_version.constrained_json:
                constrained = latest_version.constrained_json
                if isinstance(constrained, str):
                    constrained = json.loads(constrained)
                # Extract capability_boundaries or top-level list
                if isinstance(constrained, dict):
                    boundaries = constrained.get("capability_boundaries", [])
                    if isinstance(boundaries, list):
                        constraints = [str(b) for b in boundaries]
                    # Also include any explicit constraints list
                    explicit = constrained.get("constraints", [])
                    if isinstance(explicit, list):
                        constraints.extend([str(c) for c in explicit])
                elif isinstance(constrained, list):
                    constraints = [str(c) for c in constrained]
            debug["constraints_found"] = len(constraints)
        except Exception:
            logger.exception("Failed to extract constraints for resume bundle")
            debug["constraints_error"] = True

        # ── 7. Recommended next actions ─────────────────────────────
        recommended_next_actions: list[str] = []
        try:
            # From top threads
            for t in top_threads:
                if t.next_action:
                    recommended_next_actions.append(
                        f"[Thread: {t.title}] {t.next_action}"
                    )

            # From active projects (first next step each)
            for p in active_projects:
                if p.next_steps:
                    recommended_next_actions.append(
                        f"[Project: {p.name}] {p.next_steps[0]}"
                    )

            # From urgent commitments
            for c in urgent_commitments:
                due_str = c.due_date.strftime("%Y-%m-%d") if c.due_date else "no date"
                recommended_next_actions.append(
                    f"[Commitment due {due_str}] {c.commitment_text}"
                )

            debug["next_actions_generated"] = len(recommended_next_actions)
        except Exception:
            logger.exception("Failed to generate next actions for resume bundle")
            debug["next_actions_error"] = True

        # ── Assemble ────────────────────────────────────────────────
        return ResumeBundle(
            top_threads=top_threads,
            urgent_commitments=urgent_commitments,
            recent_identity_changes=recent_identity_changes,
            active_projects=active_projects,
            relevant_memories=relevant_memories,
            constraints=constraints,
            recommended_next_actions=recommended_next_actions,
            generated_at=now,
            token_budget=token_budget,
            debug_info=debug,
        )


# ── Helpers ─────────────────────────────────────────────────────────────


def _parse_json_list(value: Any) -> list[str]:
    """
    Safely parse a JSON column that should be a list of strings.
    Handles None, already-parsed lists, and JSON strings.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (json.JSONDecodeError, TypeError):
            pass
    return []


def _extract_diff_summary(diff_json: Any) -> str:
    """
    Extract a human-readable summary from the diff_from_prior_json field.
    """
    if diff_json is None:
        return "Initial version (no prior diff)"
    if isinstance(diff_json, str):
        try:
            diff_json = json.loads(diff_json)
        except (json.JSONDecodeError, TypeError):
            return str(diff_json)[:200]

    if isinstance(diff_json, dict):
        # Try common structures
        if "summary" in diff_json:
            return str(diff_json["summary"])
        # List changed fields
        changed = list(diff_json.keys())
        if changed:
            return f"Changed: {', '.join(changed[:5])}"
        return "No changes recorded"

    if isinstance(diff_json, list):
        return f"{len(diff_json)} change(s) recorded"

    return str(diff_json)[:200]
