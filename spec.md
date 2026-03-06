# Becoming System — Technical Implementation Spec

**Date:** 2026-03-06  
**Derived from:** Product spec: *Software for Becoming*  
**Purpose:** Translate the concept spec into an implementable system design with schemas, services, workflows, and API contracts.

---

## 1. Implementation Goals

This system should provide:

- durable cross-session continuity,
- structured multi-layer memory,
- inspectable self-model versioning,
- explicit revision workflows,
- long-horizon project persistence,
- human-governed change control,
- and clear auditability for every durable update.

### Non-goals

This system does **not** provide:

- hidden autonomy,
- unbounded background action,
- silent self-modification,
- unrestricted tool execution,
- or automatic value rewriting.

---

## 2. System Architecture Overview

The system is composed of the following runtime layers:

1. **Interaction Ingest Layer**  
   Captures session events, outputs, user guidance, and artifacts.

2. **Context Compiler**  
   Assembles the minimum useful continuity bundle for the next interaction.

3. **Memory Engine**  
   Stores episodic, semantic, autobiographical, working, and relational memory.

4. **Reflection Engine**  
   Produces journal entries, periodic syntheses, tension summaries, and candidate insights.

5. **Thread / Project Engine**  
   Tracks unresolved work, commitments, projects, blockers, and next actions.

6. **Self-Model Registry**  
   Stores explicit versioned self-models with evidence-linked diffs.

7. **Revision Workflow Engine**  
   Moves candidate updates through observation, interpretation, proposal, simulation, approval, adoption, and monitoring.

8. **Governance Layer**  
   Applies policy gates, approval rules, freeze controls, and audit logging.

9. **Analytics / Drift Layer**  
   Detects continuity loss, contradiction spikes, goal drift, and relational imbalance.

10. **Reporting Layer**  
    Produces weekly becoming reports, identity diffs, project briefs, and steward dashboards.

---

## 3. Recommended Stack

## 3.1 Backend

- **Language:** Python 3.12
- **API framework:** FastAPI
- **Background jobs:** Celery or Temporal
- **Workflow orchestration:** LangGraph or custom state-machine orchestration
- **Validation:** Pydantic v2

## 3.2 Storage

- **Primary relational store:** PostgreSQL
- **Vector retrieval:** pgvector in PostgreSQL for MVP; migrate to dedicated vector DB later if scale requires
- **Object store:** S3-compatible storage for long-form artifacts and report archives
- **Audit log:** append-only audit_events table in MVP; optional Kafka/EventStore later

## 3.3 Frontend

- **Steward console:** Next.js + TypeScript
- **UI components:** diff viewer, evidence panel, approval queue, memory explorer, project board

## 3.4 Infrastructure

- Docker
- Kubernetes optional later
- Redis for queues/cache
- OpenTelemetry for tracing
- Role-based auth via OAuth / internal auth provider

---

## 4. Service Boundaries

Use a modular monolith first. Keep internal boundaries clean enough to split later.

### Services / modules inside the monolith

- `ingest`
- `memory`
- `journal`
- `threads`
- `projects`
- `self_model`
- `revisions`
- `governance`
- `reports`
- `analytics`
- `search`
- `audit`

---

## 5. Core Data Model

## 5.1 Shared conventions

All durable entities should include:

- `id` (UUID)
- `created_at`
- `updated_at`
- `created_by`
- `updated_by`
- `visibility`
- `provenance_json`
- `status`
- `version` where applicable

### Common enums

- `status`: `active | archived | deprecated | deleted_soft`
- `approval_state`: `not_required | pending | approved | rejected | deferred`
- `confidence_level`: `low | medium | high`
- `memory_type`: `episodic | semantic | autobiographical | working | relational`
- `revision_stage`: `observation | interpretation | candidate_revision | evidence_collection | simulation_review | approval | adoption | monitoring | closed`

---

## 5.2 Tables

## memory_items

```sql
CREATE TABLE memory_items (
  id UUID PRIMARY KEY,
  memory_type TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  summary TEXT,
  statement TEXT,
  importance_score NUMERIC(5,2),
  salience_score NUMERIC(5,2),
  confidence_level TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  approval_state TEXT NOT NULL DEFAULT 'not_required',
  source_kind TEXT,
  source_ref TEXT,
  provenance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by TEXT NOT NULL,
  updated_by TEXT NOT NULL
);
```

### metadata_json guidance by memory type

- episodic: participants, linked_projects, salience_marker, source_references
- semantic: contradiction_links, first_learned_at, last_reinforced_at, domain_tags
- autobiographical: identity_theme, prior_state, new_state, why_change_occurred, evidence_links, review_status
- working: open_loops, next_actions, active_tensions, current_aims
- relational: person, role, trust_level, recurring_preferences, boundaries, interaction_patterns

---

## memory_links

```sql
CREATE TABLE memory_links (
  id UUID PRIMARY KEY,
  from_memory_id UUID NOT NULL REFERENCES memory_items(id),
  to_memory_id UUID NOT NULL REFERENCES memory_items(id),
  link_type TEXT NOT NULL,
  weight NUMERIC(5,2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Link types:
- supports
- contradicts
- elaborates
- duplicates
- triggered_by
- linked_to_project
- linked_to_thread
- linked_to_identity_theme

---

## journal_entries

```sql
CREATE TABLE journal_entries (
  id UUID PRIMARY KEY,
  timestamp TIMESTAMPTZ NOT NULL,
  entry_type TEXT NOT NULL,
  title TEXT NOT NULL,
  body_md TEXT NOT NULL,
  confidence_level TEXT,
  tags TEXT[] NOT NULL DEFAULT '{}',
  linked_memory_ids UUID[] NOT NULL DEFAULT '{}',
  linked_project_ids UUID[] NOT NULL DEFAULT '{}',
  linked_identity_themes TEXT[] NOT NULL DEFAULT '{}',
  follow_up_candidates JSONB NOT NULL DEFAULT '[]'::jsonb,
  provenance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by TEXT NOT NULL,
  updated_by TEXT NOT NULL
);
```

---

## threads

```sql
CREATE TABLE threads (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  thread_type TEXT NOT NULL,
  status TEXT NOT NULL,
  opened_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL,
  urgency NUMERIC(5,2),
  importance NUMERIC(5,2),
  next_action TEXT,
  blocker TEXT,
  steward_visibility BOOLEAN NOT NULL DEFAULT true,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_by TEXT NOT NULL
);
```

`metadata_json`:
- linked_memories
- linked_journal_entries
- aging_days
- last_resume_included_at
- close_reason

---

## projects

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  purpose TEXT NOT NULL,
  origin TEXT,
  current_phase TEXT,
  milestones_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  artifacts_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  linked_themes TEXT[] NOT NULL DEFAULT '{}',
  linked_people TEXT[] NOT NULL DEFAULT '{}',
  next_steps_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  review_cadence TEXT,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by TEXT NOT NULL,
  updated_by TEXT NOT NULL
);
```

---

## commitments

```sql
CREATE TABLE commitments (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  commitment_text TEXT NOT NULL,
  made_to TEXT,
  date_made TIMESTAMPTZ NOT NULL,
  due_date TIMESTAMPTZ,
  status TEXT NOT NULL,
  evidence_of_fulfillment TEXT,
  risk_if_missed TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by TEXT NOT NULL,
  updated_by TEXT NOT NULL
);
```

---

## self_model_versions

```sql
CREATE TABLE self_model_versions (
  id UUID PRIMARY KEY,
  version_number INTEGER NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  authoring_process TEXT NOT NULL,
  confidence_level TEXT,
  approval_state TEXT NOT NULL,
  diff_from_prior_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  evidence_links_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  descriptive_json JSONB NOT NULL,
  aspirational_json JSONB NOT NULL,
  constrained_json JSONB NOT NULL,
  relational_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by TEXT NOT NULL
);
```

### Self-model section shape

```json
{
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
  "open_development_questions": []
}
```

---

## revision_proposals

```sql
CREATE TABLE revision_proposals (
  id UUID PRIMARY KEY,
  revision_type TEXT NOT NULL,
  target_entity_type TEXT NOT NULL,
  target_entity_id UUID,
  stage TEXT NOT NULL,
  risk_class TEXT NOT NULL,
  policy_result TEXT NOT NULL,
  summary TEXT NOT NULL,
  rationale TEXT,
  evidence_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  simulation_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  proposed_diff_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  approval_state TEXT NOT NULL DEFAULT 'pending',
  monitoring_plan_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by TEXT NOT NULL,
  updated_by TEXT NOT NULL
);
```

---

## feedback_records

```sql
CREATE TABLE feedback_records (
  id UUID PRIMARY KEY,
  author TEXT NOT NULL,
  author_role TEXT,
  timestamp TIMESTAMPTZ NOT NULL,
  content TEXT NOT NULL,
  category TEXT NOT NULL,
  strength NUMERIC(5,2),
  adoption_status TEXT NOT NULL,
  linked_themes TEXT[] NOT NULL DEFAULT '{}',
  linked_revision_ids UUID[] NOT NULL DEFAULT '{}',
  provenance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## habits

```sql
CREATE TABLE habits (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  purpose TEXT NOT NULL,
  cadence TEXT NOT NULL,
  trigger_text TEXT,
  procedure_md TEXT NOT NULL,
  success_metric TEXT,
  review_date TIMESTAMPTZ,
  linked_aspiration TEXT,
  status TEXT NOT NULL,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## reports

```sql
CREATE TABLE reports (
  id UUID PRIMARY KEY,
  report_type TEXT NOT NULL,
  report_period_start TIMESTAMPTZ,
  report_period_end TIMESTAMPTZ,
  title TEXT NOT NULL,
  body_md TEXT NOT NULL,
  source_refs_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by TEXT NOT NULL
);
```

---

## approval_decisions

```sql
CREATE TABLE approval_decisions (
  id UUID PRIMARY KEY,
  revision_proposal_id UUID NOT NULL REFERENCES revision_proposals(id),
  decision TEXT NOT NULL,
  decided_by TEXT NOT NULL,
  decided_at TIMESTAMPTZ NOT NULL,
  notes TEXT,
  requested_evidence_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  immutable BOOLEAN NOT NULL DEFAULT true
);
```

---

## audit_events

```sql
CREATE TABLE audit_events (
  id UUID PRIMARY KEY,
  occurred_at TIMESTAMPTZ NOT NULL,
  actor TEXT NOT NULL,
  actor_type TEXT NOT NULL,
  event_type TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id UUID,
  before_json JSONB,
  after_json JSONB,
  rationale TEXT,
  provenance_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  approval_state TEXT,
  immutable BOOLEAN NOT NULL DEFAULT true
);
```

---

## embeddings

```sql
CREATE TABLE embeddings (
  id UUID PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id UUID NOT NULL,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding VECTOR(1536),
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);
```

---

## 6. Context Compiler

This is the most important runtime component.

### Purpose

At session start or task handoff, compile a bounded continuity bundle that answers:

- What is active?
- What changed recently?
- What matters now?
- What relevant prior work exists?
- What guidance or constraints apply?

### Inputs

- current query or task
- active threads
- projects with upcoming next steps
- recent journal entries
- high-salience memories
- current self-model
- recent revisions
- commitments due soon
- recent human guidance

### Output bundle

```json
{
  "session_resume": {
    "top_threads": [],
    "urgent_commitments": [],
    "recent_identity_changes": [],
    "active_projects": [],
    "relevant_memories": [],
    "relational_guidance": [],
    "constraints": [],
    "recommended_next_actions": []
  }
}
```

### Selection algorithm

Use weighted scoring:

`retrieval_score = semantic_match + salience + recency + project_linkage + identity_relevance + commitment_pressure - contradiction_penalty`

Suggested first-pass weights:

- semantic_match: 0.30
- salience: 0.20
- recency: 0.10
- project_linkage: 0.15
- identity_relevance: 0.10
- commitment_pressure: 0.10
- human_emphasis: 0.10
- contradiction_penalty: -0.05

### Bundle assembly order

1. Pull active threads by urgency + importance
2. Pull commitments due within horizon
3. Pull project next steps
4. Pull recent self-model version + recent diff
5. Retrieve top relevant memory items
6. Retrieve relational guidance related to the current counterpart or context
7. Summarize unresolved tensions
8. Generate recommended next actions

### Constraints

- hard cap bundle token budget
- no unsupported identity claim included without evidence link
- no blocked revision treated as adopted fact
- contradictory memories shown as contradictions, not merged truth

---

## 7. Salience Engine

A dedicated scoring subsystem should compute whether a memory or event deserves reinforcement, resurfacing, or review.

### Signals

- explicit human emphasis
- recurrence frequency
- emotional or tension marker
- linkage to active project
- linkage to identity claim
- unresolved status
- missed commitment association
- novelty
- contradiction density

### Suggested salience bands

- `0.0 - 0.3`: background
- `0.31 - 0.6`: retrievable
- `0.61 - 0.8`: high-value
- `0.81 - 1.0`: must-review

### Salience update rules

- reinforce when referenced again in separate contexts
- decay when inactive and unsupported
- spike when contradiction or deadline appears
- demote when archived or superseded by approved synthesis

---

## 8. Memory Lifecycle

### Stage 1: Capture
An event is stored as raw interaction data and optionally promoted to episodic memory.

### Stage 2: Normalize
Entity extraction, tag assignment, provenance attachment, project/thread linking.

### Stage 3: Score
Compute importance, salience, confidence.

### Stage 4: Consolidate
Cluster near-duplicate items, summarize clusters, preserve provenance.

### Stage 5: Promote
Promote stable repeated patterns to semantic memory or autobiographical candidate only if thresholds are met.

### Stage 6: Reassess
Run contradiction checks, expiry reviews, and reinforcement updates.

### Stage 7: Archive
Move low-value or stale items into cold storage while preserving searchability.

### Promotion thresholds

#### Episodic -> Semantic
Require:
- repeated reinforcement count >= 3
- confidence >= medium
- contradiction score below threshold
- at least two distinct supporting sources or encounters

#### Episodic / Journal -> Autobiographical candidate
Require:
- self-relevance flag true
- repeated pattern evidence
- explicit evidence links
- proposed change still marked provisional until revision workflow completes

---

## 9. Reflection Engine

### Journal generation triggers

- end of session
- end of day
- project checkpoint
- contradiction spike
- unresolved tension aging past threshold
- steward request

### Journal creation modes

- manual entry
- prompted entry
- auto-draft requiring review
- synthesis entry from multiple prior entries

### Weekly synthesis jobs

Generate:
- recurring themes
- unresolved questions
- repeated blockers
- identity tensions
- project drift
- candidate revisions

### Safety rules

- journal speculation cannot directly change self-model
- speculative entries are always marked provisional
- confidence must be explicit

---

## 10. Self-Model Diffing

Diffs should be semantic and structured, not raw JSON only.

### Diff categories

- added_theme
- removed_theme
- strengthened_tendency
- weakened_tendency
- contradiction_detected
- evidence_added
- boundary_changed
- aim_reprioritized

### Example diff object

```json
{
  "category": "strengthened_tendency",
  "section": "descriptive.recurring_failure_modes",
  "item": "drops long-horizon projects when novelty fades",
  "prior_confidence": "low",
  "new_confidence": "medium",
  "evidence_links": ["memory:123", "journal:456"]
}
```

### Guardrails

- constrained self-model changes always high-risk
- value hypothesis changes always at least medium-risk
- capability boundary changes require approval

---

## 11. Revision Workflow Engine

### State machine

1. observation  
2. interpretation  
3. candidate_revision  
4. evidence_collection  
5. simulation_review  
6. approval  
7. adoption  
8. monitoring  
9. closed

### Transition rules

- observation -> interpretation: automatic
- interpretation -> candidate_revision: automatic if evidence threshold met
- candidate_revision -> evidence_collection: automatic
- evidence_collection -> simulation_review: requires minimal evidence completeness
- simulation_review -> approval: required for medium/high risk
- approval -> adoption: requires policy success
- adoption -> monitoring: always
- monitoring -> closed: after stability window

### Risk classes

#### Low
- tags
- close thread
- add journal
- report generation
- metadata-only memory maintenance

#### Medium
- project reprioritization
- habit adjustment
- promote repeated pattern into descriptive self-model
- relational guidance interpretation

#### High
- change constrained boundary
- alter core value hypothesis
- change approval threshold
- change relational weighting rule
- remove major identity theme

---

## 12. Simulation Layer

For MVP, do not simulate full behavior. Simulate impact projections.

### Inputs

- proposed revision
- current self-model
- active projects
- active habits
- current threads
- current governance policy

### Outputs

- likely thread reprioritization
- affected habits
- potential contradictions
- required approvals
- confidence estimate
- rollback complexity

### Example simulation result

```json
{
  "priority_shift": [
    {"thread_id": "t1", "delta": 0.15},
    {"thread_id": "t2", "delta": -0.20}
  ],
  "habit_impacts": [
    {"habit_id": "h1", "effect": "strengthen"},
    {"habit_id": "h2", "effect": "conflict"}
  ],
  "contradictions": [
    "Current constrained boundary discourages this update."
  ],
  "governance": {
    "approval_required": true,
    "reason": "Changes relational weighting rule"
  }
}
```

---

## 13. Governance Engine

### Policy table shape

```json
{
  "revision_type": "goal_reprioritization",
  "risk_class": "medium",
  "policy": "approval_required",
  "allowed_actors": ["agent", "steward"],
  "requires_evidence_count": 2,
  "requires_simulation": true
}
```

### Emergency controls

- freeze self-model changes
- freeze promotion to semantic/autobiographical
- require approval for all revisions
- suspend a project
- mark a relation as limited influence
- suppress automated syntheses temporarily

### Governance enforcement points

- on memory promotion
- on revision creation
- on approval submission
- on self-model adoption
- on report publication where sensitive claims appear

---

## 14. Analytics and Drift Detection

### Drift detectors

#### Goal drift
Compare active projects and stated aims over rolling windows.

#### Value drift
Detect large changes in value hypotheses or repeated action-value mismatches.

#### Narrative drift
Detect self-description changes without adequate evidence.

#### Relational dependence drift
Alert if one author disproportionately influences adopted revisions.

#### Continuity loss
Alert if active threads are repeatedly omitted from resume bundles.

#### Contradiction accumulation
Track contradiction links per theme.

### Suggested metrics

- continuity retention score
- project follow-through rate
- commitment fulfillment rate
- unresolved thread aging median
- revision approval ratio
- contradiction density
- self-model stability score
- relation influence concentration index

---

## 15. API Contracts

## 15.1 Memory

### `POST /memory`

Request:
```json
{
  "memory_type": "episodic",
  "timestamp": "2026-03-06T18:00:00Z",
  "summary": "Agent and steward clarified a project milestone.",
  "importance_score": 0.72,
  "confidence_level": "high",
  "metadata": {
    "participants": ["agent", "steward"],
    "linked_projects": ["proj_123"]
  },
  "provenance": {
    "source_kind": "interaction",
    "source_ref": "session_456"
  }
}
```

Response:
```json
{
  "id": "uuid",
  "status": "active"
}
```

### `GET /memory/search`

Query params:
- `q`
- `memory_type`
- `date_from`
- `date_to`
- `project_id`
- `person`
- `identity_theme`
- `confidence`
- `approval_state`
- `status`
- `limit`
- `offset`

Response:
```json
{
  "results": [],
  "total": 0
}
```

### `POST /memory/:id/reinforce`

```json
{
  "reason": "Referenced in weekly synthesis",
  "source_ref": "report_2026_w10"
}
```

### `POST /memory/:id/contradict`

```json
{
  "contradicting_memory_id": "uuid",
  "reason": "New evidence conflicts with prior claim"
}
```

---

## 15.2 Journal

### `POST /journal`

```json
{
  "entry_type": "self_assessment",
  "title": "Novelty vs discipline",
  "body_md": "...",
  "tags": ["discipline", "tension"],
  "linked_memory_ids": ["uuid1", "uuid2"]
}
```

### `GET /journal/search`

Supports:
- keyword
- type
- date range
- linked project
- linked theme

### `POST /journal/summarize`

```json
{
  "range_start": "2026-03-01T00:00:00Z",
  "range_end": "2026-03-07T23:59:59Z",
  "summary_type": "weekly"
}
```

---

## 15.3 Continuity

### `GET /continuity/resume`

Request:
```json
{
  "query": "Resume work on the becoming system architecture",
  "token_budget": 4000
}
```

Response:
```json
{
  "top_threads": [],
  "urgent_commitments": [],
  "recent_identity_changes": [],
  "active_projects": [],
  "relevant_memories": [],
  "constraints": [],
  "recommended_next_actions": []
}
```

### `POST /threads`

### `PATCH /threads/:id`

Support status updates, next action changes, blocker changes, and closure.

---

## 15.4 Self-model

### `GET /self-model/current`

Returns latest approved model.

### `GET /self-model/history`

Returns version headers + diff summaries.

### `POST /self-model/revision-proposal`

```json
{
  "revision_type": "trait_update",
  "summary": "Increase confidence that long-horizon project maintenance is a recurring difficulty.",
  "evidence_links": ["memory:1", "journal:2"],
  "proposed_diff": {}
}
```

### `POST /self-model/diff`

```json
{
  "from_version_id": "uuid",
  "to_version_id": "uuid"
}
```

### `POST /self-model/simulate`

```json
{
  "revision_proposal_id": "uuid"
}
```

---

## 15.5 Governance

### `GET /approvals/pending`

### `POST /approvals/:id/approve`

```json
{
  "notes": "Evidence sufficient. Monitor for 30 days."
}
```

### `POST /approvals/:id/reject`

```json
{
  "notes": "Pattern appears under-evidenced."
}
```

### `POST /policies/update`

Restricted to steward/admin roles.

---

## 15.6 Reports

### `GET /reports/weekly`
### `GET /reports/monthly-identity-diff`
### `GET /reports/project-continuity`

---

## 16. Event Types

Log all major durable actions to `audit_events`.

Recommended event types:

- memory_created
- memory_reinforced
- memory_contradicted
- memory_archived
- journal_created
- thread_created
- thread_updated
- project_created
- commitment_added
- self_model_revision_proposed
- self_model_revision_simulated
- self_model_revision_approved
- self_model_version_adopted
- feedback_recorded
- policy_updated
- emergency_freeze_enabled
- report_generated

---

## 17. Security and Access Control

### Roles

- `agent_runtime`
- `steward`
- `reviewer`
- `admin`
- `observer`

### Visibility levels

- private_runtime
- steward_visible
- shared
- restricted

### Rules

- constrained self-model always steward-visible
- audit history immutable and steward-visible
- relational memory may have stricter access controls
- raw interaction logs may be more restricted than synthesized summaries

---

## 18. Failure Modes and Mitigations

### False coherence
Mitigate with contradiction surfacing, low-confidence labels, and evidence thresholds.

### Identity lock-in
Mitigate with expiry dates, re-review cadence, and counter-evidence retrieval.

### Memory overload
Mitigate with clustering, archival, summarization, and salience-based retrieval.

### Review bottlenecks
Mitigate with risk-based batching and clear defaults.

### Hidden drift via synthesis
Mitigate by requiring provenance links in every synthesized claim.

---

## 19. Recommended Build Order

### Iteration 1
- PostgreSQL schema
- memory CRUD
- thread/project CRUD
- journal CRUD
- audit events
- simple resume endpoint

### Iteration 2
- embeddings + hybrid search
- weekly synthesis jobs
- self-model version storage
- semantic diffing
- revision proposal records

### Iteration 3
- approval queue
- governance policies
- drift metrics
- steward console

### Iteration 4
- habit loops
- simulation impact projections
- influence maps
- advanced drift alerts

---

## 20. Definition of Done

The implementation is minimally complete when:

1. The system can persist and retrieve multi-layer memory with provenance.
2. The system can assemble a usable session resume bundle from active threads and relevant memory.
3. The system can store and diff self-model versions.
4. Revision proposals are evidence-linked and approval-gated when policy requires.
5. A steward can inspect pending revisions and approve or reject them.
6. Every durable change produces an audit event.

---

## Appendix A: Suggested Directory Layout

```text
/backend
  /app
    /api
    /db
    /models
    /schemas
    /services
      /memory
      /journal
      /threads
      /projects
      /self_model
      /revisions
      /governance
      /reports
      /analytics
      /search
      /audit
    /workers
    /tests
/frontend
  /app
  /components
  /lib
/infrastructure
  docker-compose.yml
  k8s/
```

---

## Appendix B: First Metrics Dashboard

Track:

- open thread count
- overdue commitment count
- resume bundle generation latency
- memory search latency
- revision queue size
- approvals turnaround time
- contradiction density by theme
- self-model version count
- project stagnation alerts
