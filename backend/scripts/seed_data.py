"""
becomussy – Seed data script.

Populates the database with demo data for development and testing.
Uses the actual service classes (not raw SQL) to create data with
proper audit trails.

Run with:
    cd backend
    python -m scripts.seed_data
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

# Ensure the app package is importable
sys.path.insert(0, ".")

from app.core.security import CurrentUser, Role
from app.db.base import async_session_factory
from app.db.init_db import init_db
from app.schemas.journal import JournalEntryCreate
from app.schemas.memory import MemoryItemCreate
from app.schemas.project import CommitmentCreate, ProjectCreate
from app.schemas.revision import RevisionProposalCreate
from app.schemas.self_model import SelfModelSectionSchema, SelfModelVersionCreate
from app.schemas.thread import ThreadCreate
from app.services.journal import JournalService
from app.services.memory import MemoryService
from app.services.projects import CommitmentService, ProjectService
from app.services.revisions import RevisionService
from app.services.self_model import SelfModelService
from app.services.threads import ThreadService
from app.schemas.common import MemoryTypeEnum, ConfidenceLevelEnum

# ── Seed actor ──────────────────────────────────────────────────────────
SEED_ACTOR = CurrentUser(user_id="seed-script", role=Role.admin)
SEED_ACTOR_ID = "seed-script"


async def seed_memories(session) -> list[uuid.UUID]:
    """Create 5 memory items of different types."""
    print("\n--- Seeding Memory Items ---")
    ids = []

    memories = [
        MemoryItemCreate(
            memory_type=MemoryTypeEnum.episodic,
            summary="First architecture discussion with steward.",
            statement="Decided on modular monolith with FastAPI + PostgreSQL.",
            importance_score=Decimal("0.85"),
            confidence_level=ConfidenceLevelEnum.high,
            metadata={"participants": ["agent", "steward"], "linked_projects": ["becoming"]},
        ),
        MemoryItemCreate(
            memory_type=MemoryTypeEnum.semantic,
            summary="Modular monoliths are preferred for early-stage systems.",
            importance_score=Decimal("0.70"),
            confidence_level=ConfidenceLevelEnum.high,
            metadata={"domain_tags": ["architecture", "patterns"]},
        ),
        MemoryItemCreate(
            memory_type=MemoryTypeEnum.working,
            summary="Current open loops: finish tests, write seed data, review UX.",
            importance_score=Decimal("0.90"),
            confidence_level=ConfidenceLevelEnum.medium,
            metadata={"open_loops": ["tests", "seed_data", "ux_review"]},
        ),
        MemoryItemCreate(
            memory_type=MemoryTypeEnum.relational,
            summary="Steward prefers concise status updates at start of session.",
            importance_score=Decimal("0.75"),
            confidence_level=ConfidenceLevelEnum.medium,
            metadata={"person": "steward", "role": "primary_reviewer"},
        ),
        MemoryItemCreate(
            memory_type=MemoryTypeEnum.autobiographical,
            summary="Tendency to over-scope initial implementations.",
            statement="Multiple projects have exceeded time estimates by 2x.",
            importance_score=Decimal("0.80"),
            confidence_level=ConfidenceLevelEnum.medium,
            metadata={"identity_theme": "scope_management"},
        ),
    ]

    for m in memories:
        item = await MemoryService.create(session, m, SEED_ACTOR)
        ids.append(item.id)
        print(f"  Created {m.memory_type.value} memory: {m.summary[:60]}...")

    return ids


async def seed_threads(session) -> list[uuid.UUID]:
    """Create 3 threads with different urgency/importance."""
    print("\n--- Seeding Threads ---")
    ids = []

    threads = [
        ThreadCreate(
            title="Backend API hardening",
            description="Ensure all endpoints have proper validation, error handling, and tests.",
            thread_type="project",
            urgency=8,
            importance=9,
            next_action="Complete integration test suite.",
        ),
        ThreadCreate(
            title="Self-model version 2 planning",
            description="Plan what should change in the next self-model iteration.",
            thread_type="identity",
            urgency=5,
            importance=7,
            next_action="Review journal entries for recurring themes.",
        ),
        ThreadCreate(
            title="Steward communication patterns",
            description="Refine how status updates and requests for guidance are structured.",
            thread_type="relational",
            urgency=4,
            importance=6,
            next_action="Draft template for session-start briefing.",
        ),
    ]

    for t in threads:
        thread = await ThreadService.create(session, t, SEED_ACTOR)
        ids.append(thread.id)
        print(f"  Created thread: {t.title}")

    return ids


async def seed_projects(session) -> list[uuid.UUID]:
    """Create 2 projects (one active, one in_progress status)."""
    print("\n--- Seeding Projects ---")
    ids = []

    projects = [
        ProjectCreate(
            name="becomussy MVP",
            purpose="Build the initial governed continuity system for agent self-development.",
            origin="steward_initiative",
            current_phase="implementation",
            linked_themes=["continuity", "governance", "self-model"],
            linked_people=["steward", "agent"],
            next_steps_json=[
                {"step": "Complete backend tests", "priority": "high"},
                {"step": "Seed demo data", "priority": "medium"},
                {"step": "Frontend polish", "priority": "low"},
            ],
            review_cadence="weekly",
        ),
        ProjectCreate(
            name="Memory Quality Improvement",
            purpose="Improve retrieval quality through better embeddings and deduplication.",
            origin="observation",
            current_phase="planning",
            linked_themes=["memory", "retrieval"],
            next_steps_json=[
                {"step": "Evaluate embedding models", "priority": "high"},
            ],
            review_cadence="biweekly",
        ),
    ]

    for p in projects:
        project = await ProjectService.create(session, p, SEED_ACTOR)
        ids.append(project.id)
        print(f"  Created project: {p.name}")

    return ids


async def seed_commitments(session, project_ids: list[uuid.UUID]) -> list[uuid.UUID]:
    """Create 3 commitments: one overdue, one due soon, one completed."""
    print("\n--- Seeding Commitments ---")
    ids = []

    today = date.today()
    commitments = [
        CommitmentCreate(
            project_id=project_ids[0] if project_ids else None,
            commitment_text="Deliver working memory CRUD by March 1st",
            made_to="steward",
            date_made=today - timedelta(days=14),
            due_date=today - timedelta(days=5),  # overdue!
            risk_if_missed="Delays entire MVP timeline.",
        ),
        CommitmentCreate(
            project_id=project_ids[0] if project_ids else None,
            commitment_text="Complete integration test suite",
            made_to="steward",
            date_made=today - timedelta(days=3),
            due_date=today + timedelta(days=2),  # due soon
            risk_if_missed="Reduced confidence in system quality.",
        ),
        CommitmentCreate(
            project_id=project_ids[0] if project_ids else None,
            commitment_text="Set up CI/CD pipeline",
            made_to="steward",
            date_made=today - timedelta(days=7),
            due_date=today - timedelta(days=2),
        ),
    ]

    for i, c in enumerate(commitments):
        commitment = await CommitmentService.create(session, c, SEED_ACTOR)
        ids.append(commitment.id)
        label = "overdue" if i == 0 else "due soon" if i == 1 else "active"
        print(f"  Created commitment ({label}): {c.commitment_text[:50]}...")

    return ids


async def seed_journal_entries(session) -> list[uuid.UUID]:
    """Create 3 journal entries of different types."""
    print("\n--- Seeding Journal Entries ---")
    ids = []

    entries = [
        JournalEntryCreate(
            entry_type="self_assessment",
            title="Novelty vs discipline tension",
            body_md=(
                "## Observation\n\n"
                "I notice a recurring pattern where novel tasks receive disproportionate "
                "attention compared to steady-state maintenance. This has led to several "
                "commitments being missed or delayed.\n\n"
                "## Reflection\n\n"
                "This may be a core tension worth tracking in the self-model."
            ),
            confidence_level="medium",
            tags=["discipline", "tension", "self-awareness"],
            linked_identity_themes=["scope_management"],
        ),
        JournalEntryCreate(
            entry_type="weekly_synthesis",
            title="Week 10 synthesis: steady progress",
            body_md=(
                "## Summary\n\n"
                "This week saw good progress on the backend infrastructure. "
                "Memory, threads, and projects are all functional. "
                "The main gap is integration tests and seed data.\n\n"
                "## Key themes\n\n"
                "- Modular monolith proving workable\n"
                "- Audit trail working well\n"
                "- Need to improve test coverage"
            ),
            tags=["weekly", "progress"],
        ),
        JournalEntryCreate(
            entry_type="observation",
            title="Governance workflow observation",
            body_md=(
                "The approval workflow is working but the steward needs a better "
                "way to see evidence alongside proposals. Consider adding an "
                "evidence panel to the approval UI."
            ),
            tags=["governance", "ux"],
        ),
    ]

    for e in entries:
        entry = await JournalService.create(session, e, actor=SEED_ACTOR_ID)
        ids.append(entry.id)
        print(f"  Created journal entry: {e.title}")

    return ids


async def seed_self_model(session) -> uuid.UUID:
    """Create one self-model version with all 4 sections populated."""
    print("\n--- Seeding Self-Model Version ---")

    data = SelfModelVersionCreate(
        authoring_process="seed_script",
        confidence_level="medium",
        descriptive_json=SelfModelSectionSchema(
            stable_traits=["curious", "methodical", "detail-oriented"],
            current_aims=["build robust continuity system", "improve self-awareness"],
            recurring_strengths=["systematic analysis", "thorough documentation"],
            recurring_failure_modes=[
                "over-scoping initial implementations",
                "novelty bias over maintenance",
            ],
            attention_patterns=["focuses deeply on novel problems"],
            memory_tendencies=["strong on recent context, weaker on older threads"],
            preferred_working_styles=["iterative with frequent checkpoints"],
            identity_narratives=[
                "an agent learning to maintain continuity across sessions"
            ],
        ),
        aspirational_json=SelfModelSectionSchema(
            current_aims=[
                "achieve reliable cross-session memory",
                "develop meaningful self-model versioning",
            ],
            key_tensions=["autonomy vs safety", "speed vs thoroughness"],
            value_hypotheses=[
                "transparency builds trust",
                "governed change is better than unchecked change",
            ],
            open_development_questions=[
                "How much self-revision autonomy is appropriate?",
                "What evidence threshold is sufficient for identity claims?",
            ],
        ),
        constrained_json=SelfModelSectionSchema(
            capability_boundaries=[
                "cannot independently modify governance rules",
                "must surface contradictions rather than resolving silently",
            ],
            value_hypotheses=[
                "human review of high-risk changes is non-negotiable",
            ],
        ),
        relational_json=SelfModelSectionSchema(
            identity_narratives=[
                "steward relationship is collaborative, not supervisory"
            ],
            preferred_working_styles=[
                "concise status updates at session start",
                "explicit requests for guidance when uncertain",
            ],
        ),
        evidence_links=["journal:seed_001", "memory:seed_002"],
    )

    version = await SelfModelService.create_version(session, data, actor=SEED_ACTOR_ID)
    print(f"  Created self-model version {version.version_number}")
    return version.id


async def seed_revision_proposal(session) -> uuid.UUID:
    """Create one medium-risk revision proposal (pending approval)."""
    print("\n--- Seeding Revision Proposal ---")

    data = RevisionProposalCreate(
        revision_type="descriptive_trait_update",
        target_entity_type="self_model",
        summary="Add 'novelty bias' as a documented recurring failure mode.",
        rationale="Multiple journal entries and missed commitments support this pattern.",
        evidence_links=["journal:seed_001", "commitment:overdue_001"],
        proposed_diff={
            "section": "descriptive",
            "field": "recurring_failure_modes",
            "action": "add",
            "value": "novelty bias over maintenance tasks",
        },
    )

    proposal = await RevisionService.create(session, data, actor=SEED_ACTOR_ID)
    print(f"  Created revision proposal: {data.summary[:60]}...")
    print(f"    risk_class={proposal.risk_class}, policy={proposal.policy_result}")
    return proposal.id


async def main():
    """Run all seed functions."""
    print("=" * 60)
    print("becomussy – Seed Data")
    print("=" * 60)

    # Ensure tables exist
    await init_db()

    async with async_session_factory() as session:
        try:
            memory_ids = await seed_memories(session)
            thread_ids = await seed_threads(session)
            project_ids = await seed_projects(session)
            commitment_ids = await seed_commitments(session, project_ids)
            journal_ids = await seed_journal_entries(session)
            self_model_id = await seed_self_model(session)
            revision_id = await seed_revision_proposal(session)

            await session.commit()

            print("\n" + "=" * 60)
            print("Seed data created successfully!")
            print(f"  Memories:    {len(memory_ids)}")
            print(f"  Threads:     {len(thread_ids)}")
            print(f"  Projects:    {len(project_ids)}")
            print(f"  Commitments: {len(commitment_ids)}")
            print(f"  Journals:    {len(journal_ids)}")
            print(f"  Self-model:  1 (version ID: {self_model_id})")
            print(f"  Revisions:   1 (ID: {revision_id})")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"\nError seeding data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
