# becomussy — Architecture Notes

How the implementation maps to the specification and build plan.

## Spec-to-Code Mapping

| Spec Section | Service Module | Description |
|---|---|---|
| 2. System Architecture: Memory Engine | `services/memory/` | CRUD, search, reinforce, contradict for multi-layer memory |
| 2. System Architecture: Thread/Project Engine | `services/threads/`, `services/projects/` | Thread, project, and commitment lifecycle |
| 2. System Architecture: Reflection Engine | `services/journal/` | Journal entries with search, linked entities, summarization |
| 2. System Architecture: Self-Model Registry | `services/self_model/` | Versioned self-model storage, semantic diffing |
| 2. System Architecture: Revision Workflow | `services/revisions/` | Proposal creation, risk classification, stage transitions |
| 2. System Architecture: Governance Layer | `services/governance/` | Approvals, policy checks, freeze controls |
| 2. System Architecture: Context Compiler | `services/search/context_compiler.py` | Resume bundle assembly |
| 8. Audit Events | `services/audit/` | Immutable audit trail for all durable changes |
| 2. System Architecture: Search | `services/search/` | Keyword-based memory search (MVP); vector search deferred |

## Plan.md Ticket Coverage

### Covered by MVP

| Epic | Tickets | Status |
|---|---|---|
| **A: Platform Foundations** | A1 (monorepo), A2 (Docker Compose), A3 (migrations), A4 (auth middleware), A5 (audit writer), A6 (health check) | Done |
| **B: Memory Engine v1** | B1-B6 (schema, CRUD, search, filters, provenance), B8 (reinforce), B9 (contradict) | Done |
| **C: Threads/Projects v1** | C1-C6 (schema, CRUD for threads, projects, commitments) | Done |
| **D: Context Compiler** | D1-D8 (resume bundle schema, assembly, token budget) | Done |
| **E: Journal System** | E1-E4, E6 (schema, CRUD, search, types, linked entities) | Done |
| **F: Self-Model Registry** | F1-F5 (schema, JSON structure, current, history, diff engine) | Done |
| **G: Revision Proposals** | G1-G3, G5-G10 (schema, proposal creation, stages, approvals, policy, freeze) | Done |

### Deferred to Post-MVP

| Epic | Tickets | Notes |
|---|---|---|
| **B: Memory Engine** | B7 (steward memory explorer view) | Frontend feature |
| **C: Threads/Projects** | C7-C9 (dashboard panels, overdue highlighting UI) | Frontend features |
| **D: Context Compiler** | D9 (bundle debug view) | Partial: debug endpoint exists, no UI |
| **E: Journal** | E5 (reflection prompts), E7-E9 (UI, weekly synthesis job) | AI features and frontend |
| **F: Self-Model** | F6-F7 (diff UI, evidence-link rendering) | Frontend features |
| **G: Governance** | G4 (evidence panel UI) | Frontend feature |
| **H: Search Quality** | H1-H9 (embeddings, hybrid search, dedup, archival) | Post-MVP phase |
| **I: Reporting** | I1-I9 (reports, analytics, dashboards) | Post-MVP phase |
| **J: Habits** | J1-J7 (habits, recurring reviews) | Post-MVP phase |
| **K: Simulation** | K1-K6 (impact projections, conflict detection) | Post-MVP phase |

## Modular Monolith Structure

The backend follows a modular monolith pattern as recommended by the spec (Section 4):

```
app/
  services/
    memory/       -> Owns memory_items, memory_links
    threads/      -> Owns threads
    projects/     -> Owns projects, commitments
    journal/      -> Owns journal_entries
    self_model/   -> Owns self_model_versions
    revisions/    -> Owns revision_proposals
    governance/   -> Owns approval_decisions
    search/       -> Cross-cutting: context compiler, search service
    audit/        -> Cross-cutting: immutable audit log
```

Each service module:
- Has its own `__init__.py` with the primary service class
- Uses static methods for a stateless, functional style
- Receives an `AsyncSession` and returns domain objects
- Never directly imports from other service modules (except `audit`)
- Communicates with the rest of the system only through the database

## Migration Chain

```
0001_create_core_tables     -> memory_items, memory_links, threads, projects, commitments, audit_events
0002_create_governance      -> approval_decisions, embeddings
0003_create_reflection      -> journal_entries, self_model_versions, revision_proposals
```

All migrations use Alembic with a linear revision chain.

## Audit Strategy

Every write operation across all services calls `AuditService.log_event()` to create an immutable `audit_events` row. The audit record includes:

- **occurred_at**: Timestamp of the event
- **actor / actor_type**: Who performed the action
- **event_type**: What happened (e.g., `memory_created`, `self_model_revision_approved`)
- **entity_type / entity_id**: What was affected
- **before_json / after_json**: State snapshots for change tracking
- **rationale**: Human-readable reason (when available)
- **provenance_json**: Source tracking metadata
- **immutable**: Always `true` (audit records cannot be modified)

Audit events are queryable via `GET /api/v1/audit` with filters by entity, event type, and actor.

## Approval Workflow

The revision proposal lifecycle follows the state machine from spec Section 11:

```
observation -> interpretation -> candidate_revision -> evidence_collection
    -> simulation_review -> approval -> adoption -> monitoring -> closed
```

### Risk Classification

| Target | Revision Type Keywords | Risk Class |
|---|---|---|
| thread, project | (any) | low |
| self_model | constrained, value, boundary | high |
| self_model | descriptive, trait, tendency | medium |
| (other) | (any) | medium (default) |

### Policy Rules

| Risk Class | Policy | Evidence Required | Simulation Required |
|---|---|---|---|
| low | auto_approve | 0 | No |
| medium | approval_required | 2 | No |
| high | approval_required | 3 | Yes |

### Emergency Freeze Controls

Three freeze types are available (MVP: in-memory state):
- `self_model`: Freeze all self-model changes
- `promotions`: Freeze memory promotions
- `all_revisions`: Freeze all revision proposals

Freezes are toggled via `POST /api/v1/approvals/freeze` (steward/admin only) and logged as audit events.

## Testing Strategy

### Unit Tests (`tests/unit/`)
- **test_diff_engine.py**: Self-model diff logic (added/removed themes, cross-section)
- **test_risk_classification.py**: Risk classification rules and policy determination
- **test_policy_check.py**: Governance policy evaluation

### Integration Tests (`tests/integration/`)
- **test_memory_flow.py**: Memory CRUD lifecycle with audit verification
- **test_thread_project_flow.py**: Thread and project CRUD with commitments
- **test_revision_approval_flow.py**: Proposal creation, approval/rejection, freeze controls
- **test_self_model_flow.py**: Version creation, diffing, history
- **test_resume_bundle.py**: Context compiler with seeded data

All integration tests use transactional isolation (rollback after each test) for repeatability.
