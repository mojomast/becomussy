nan# Becoming System — Prioritized MVP Build Plan

**Date:** 2026-03-06  
**Purpose:** Turn the product concept into a phased execution plan with priorities, tickets, recommended stack, and success criteria.

---

## 1. Build Strategy

The right way to build this system is:

- start with continuity, not full self-revision;
- make every durable update inspectable from day one;
- keep the first version human-legible;
- defer complex simulation until useful continuity already works.

### Guiding rule

Do **not** start with “AI self-modification.”  
Start with:

- memory,
- threads,
- journals,
- a self-model file,
- and an approval queue.

That gives you a real system without taking on the hardest risks first.

---

## 2. Recommended MVP Scope

Build these five capabilities first:

1. **Persistent memory store**
2. **Reflection journal**
3. **Thread + project continuity tracker**
4. **Versioned self-model with diffing**
5. **Approval queue for self-revision proposals**

### Why these five

Together they create:

- cross-session continuity,
- visible accumulation,
- explicit unfinished work,
- early reflective development,
- and governed change.

Without them, the rest is mostly orchestration around missing foundations.

---

## 3. Recommended Stack for MVP

### Backend
- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy or SQLModel

### Storage
- PostgreSQL
- pgvector
- S3-compatible object storage for long-form reports/artifacts

### Background jobs
- Celery + Redis, or a lightweight cron/job runner initially

### Frontend
- Next.js + TypeScript
- Minimal dashboard UI

### Auth
- basic role-based auth: steward, reviewer, runtime

### Hosting
- Docker Compose for dev
- single cloud environment for staging

---

## 4. MVP Principles

### Principle 1: Keep the first system inspectable
Every write should be visible in a UI or queryable via API.

### Principle 2: Separate capture from interpretation
Store raw events and derived interpretations separately.

### Principle 3: Keep identity updates draft-first
No self-model change should skip the proposal step.

### Principle 4: Prefer a modular monolith
Do not begin with microservices.

### Principle 5: Use hybrid retrieval early
Keyword + vector retrieval will beat either alone.

---

## 5. Phase Plan

## Phase 0 — Foundations
**Goal:** establish the platform skeleton and data model.

### Deliverables
- repository setup
- local dev environment
- PostgreSQL schema migrations
- audit event infrastructure
- auth roles
- API skeleton
- basic admin/steward shell UI

### Exit criteria
- services boot locally
- DB migrations run cleanly
- authenticated requests work
- audit events can be written and viewed

### Priority
P0

---

## Phase 1 — Minimal Continuity System
**Goal:** the agent can resume work across sessions.

### Features
- episodic memory CRUD
- working continuity memory
- threads CRUD
- project CRUD
- commitments CRUD
- session resume bundle v1
- simple search by keyword and filter
- basic steward memory/project viewer

### What to exclude
- semantic promotion automation
- advanced drift detection
- simulation
- trust weighting

### Exit criteria
- user can create and retrieve threads/projects
- session resume returns active threads + next actions
- important session facts can be stored with provenance
- steward can inspect stored artifacts

### Priority
P0

---

## Phase 2 — Reflective Growth Layer
**Goal:** reflective accumulation begins.

### Features
- journal CRUD
- journal prompts
- end-of-session reflection flow
- weekly synthesis job
- self-model current version storage
- self-model history view
- semantic diffing between self-model versions
- revision proposals with evidence links

### Exit criteria
- system can generate weekly summary
- self-model versions can be compared
- revision proposals are evidence-linked
- journal entries can link to memories and threads

### Priority
P0

---

## Phase 3 — Governance Layer
**Goal:** meaningful revisions become reviewable and controllable.

### Features
- approval queue
- revision risk classification
- policy engine v1
- steward approval/reject/defer actions
- emergency freeze controls
- audit-linked decision history

### Exit criteria
- medium/high risk revisions cannot be adopted without review
- steward can inspect evidence before deciding
- freeze controls work
- approval history is immutable

### Priority
P1

---

## Phase 4 — Memory Quality Layer
**Goal:** improve retrieval usefulness and information hygiene.

### Features
- embeddings and semantic retrieval
- hybrid search
- memory deduplication assistance
- contradiction linking
- archival and decay rules
- salience scoring v1

### Exit criteria
- resume bundle quality improves measurably
- duplicate memory clutter decreases
- contradiction links can be viewed
- stale low-value memories can be archived

### Priority
P1

---

## Phase 5 — Practice and Analytics Layer
**Goal:** development becomes structured practice.

### Features
- habits
- recurring review jobs
- commitment audits
- continuity metrics
- basic drift alerts
- project stagnation detection

### Exit criteria
- recurring practices can be configured
- missed commitments surface in reports
- basic drift metrics appear in dashboard

### Priority
P2

---

## Phase 6 — Sandbox / Simulation Layer
**Goal:** major changes can be previewed before adoption.

### Features
- revision impact projection
- thread reprioritization preview
- habit conflict preview
- governance implication preview

### Exit criteria
- major revision proposals can be simulated
- simulation results appear in approval UI
- no simulation output is treated as adopted fact

### Priority
P3

---

## 6. Backlog by Epic

## Epic A — Platform Foundations

### Tickets
- A1. Create monorepo with backend/frontend/infrastructure folders
- A2. Add Docker Compose for app, db, redis
- A3. Set up PostgreSQL migrations
- A4. Add auth and role middleware
- A5. Implement audit event writer
- A6. Add healthcheck and observability basics

### Priority
P0

---

## Epic B — Memory Engine v1

### Tickets
- B1. Create `memory_items` schema
- B2. Implement `POST /memory`
- B3. Implement `GET /memory/:id`
- B4. Implement `GET /memory/search`
- B5. Support memory filters by type/date/project/person/status
- B6. Attach provenance to every memory write
- B7. Build steward memory explorer view
- B8. Add memory reinforcement endpoint
- B9. Add contradiction link endpoint

### Priority
P0 for B1-B7, P1 for B8-B9

---

## Epic C — Threads and Projects v1

### Tickets
- C1. Create `threads` schema
- C2. Create `projects` schema
- C3. Create `commitments` schema
- C4. Implement thread CRUD
- C5. Implement project CRUD
- C6. Implement commitment CRUD
- C7. Build “active threads” dashboard panel
- C8. Build project detail view with milestones and next steps
- C9. Add overdue commitment highlighting

### Priority
P0

---

## Epic D — Context Compiler / Resume Bundle

### Tickets
- D1. Define resume bundle schema
- D2. Implement active thread selection logic
- D3. Add urgent commitments inclusion
- D4. Add recent project next steps inclusion
- D5. Add recent memory retrieval logic
- D6. Add constraints section from self-model/governance
- D7. Implement `GET /continuity/resume`
- D8. Add token-budget-aware truncation
- D9. Add bundle debug view for steward

### Priority
P0

---

## Epic E — Journal System

### Tickets
- E1. Create `journal_entries` schema
- E2. Implement `POST /journal`
- E3. Implement `GET /journal/search`
- E4. Add journal type enums
- E5. Add end-of-session reflection prompt flow
- E6. Add linked memory/thread/project support
- E7. Build journal list/detail UI
- E8. Implement weekly synthesis job
- E9. Store weekly synthesis as report + journal artifact

### Priority
P0 for E1-E7, P1 for E8-E9

---

## Epic F — Self-Model Registry

### Tickets
- F1. Create `self_model_versions` schema
- F2. Define self-model JSON structure
- F3. Implement `GET /self-model/current`
- F4. Implement `GET /self-model/history`
- F5. Implement self-model diff engine
- F6. Build side-by-side diff UI
- F7. Add evidence-link rendering in diff view

### Priority
P0

---

## Epic G — Revision Proposals and Approvals

### Tickets
- G1. Create `revision_proposals` schema
- G2. Implement `POST /self-model/revision-proposal`
- G3. Add proposal stages and status transitions
- G4. Build evidence panel
- G5. Create `approval_decisions` schema
- G6. Implement approvals endpoints
- G7. Build pending approvals queue
- G8. Add approve/reject/defer actions
- G9. Add policy checks before adoption
- G10. Add emergency freeze control

### Priority
P1

---

## Epic H — Search and Retrieval Quality

### Tickets
- H1. Add pgvector extension
- H2. Create embeddings table
- H3. Embed memory and journal chunks
- H4. Implement hybrid retrieval
- H5. Add search scoring debug logging
- H6. Add deduplication candidate finder
- H7. Add contradiction surfacing in results
- H8. Add archival state and archive job
- H9. Add salience score computation v1

### Priority
P1

---

## Epic I — Reporting and Analytics

### Tickets
- I1. Create `reports` schema
- I2. Implement weekly becoming report
- I3. Implement monthly identity diff report
- I4. Implement project continuity report
- I5. Add continuity retention metric
- I6. Add commitment fulfillment metric
- I7. Add unresolved thread aging metric
- I8. Add project stagnation detector
- I9. Build analytics dashboard widgets

### Priority
P1/P2

---

## Epic J — Habits and Practice Loops

### Tickets
- J1. Create `habits` schema
- J2. Implement habit CRUD
- J3. Implement recurring review scheduler
- J4. Add commitment audit job
- J5. Add contradiction review job
- J6. Add monthly self-model comparison reminder
- J7. Build habit status dashboard

### Priority
P2

---

## Epic K — Simulation Layer

### Tickets
- K1. Define simulation input schema
- K2. Define impact projection output schema
- K3. Implement project/thread reprioritization preview
- K4. Add habit conflict detection
- K5. Add governance implication detection
- K6. Expose simulation output in approval UI

### Priority
P3

---

## 7. Detailed MVP Ticket Order

This is the order I would actually execute:

### Sprint 1
- A1, A2, A3, A4
- B1, B2
- C1, C2, C3
- D1

### Sprint 2
- B3, B4, B5, B6
- C4, C5, C6
- D2, D3, D4
- basic frontend shell

### Sprint 3
- D5, D6, D7
- C7, C8, C9
- B7
- audit event viewer

### Sprint 4
- E1, E2, E3, E4, E6
- F1, F2, F3

### Sprint 5
- E5, E7, E8
- F4, F5, F6, F7
- G1, G2

### Sprint 6
- G3, G4, G5, G6, G7, G8, G9, G10
- polish, testing, launch hardening

That gets you a credible MVP.

---

## 8. Acceptance Criteria by Capability

## Memory
- can persist memory items with provenance
- can search memory items by filters
- can retrieve memory details reliably
- writes generate audit events

## Threads / Projects
- can create, update, close, and inspect threads
- can create projects and commitments
- overdue commitments are visible

## Resume Bundle
- returns active threads, next actions, recent relevant memory, and due commitments
- stays within configured token budget
- can be debugged and inspected

## Journal
- can write linked journal entries
- can search journal entries
- can produce at least one weekly synthesis output

## Self-Model
- stores versioned model snapshots
- computes meaningful diff categories
- shows evidence links per change

## Revision / Approval
- proposals can be created and staged
- high-risk changes cannot be adopted without approval
- approval actions are immutable and auditable

---

## 9. Team Shape

Minimum practical team:

- 1 backend engineer
- 1 frontend engineer
- 1 product-minded technical lead
- optional designer part-time
- optional ML/retrieval engineer after Phase 2

For a solo builder, cut UI scope aggressively and focus on API + simple admin screens.

---

## 10. Testing Strategy

### Unit tests
- scoring
- diff logic
- policy enforcement
- stage transitions
- archival rules

### Integration tests
- create memory -> retrieve in resume bundle
- create revision -> approval required -> adoption succeeds
- freeze policy -> adoption blocked
- weekly synthesis -> report stored

### Evaluation tests
- resume bundle relevance
- contradiction surfacing quality
- self-model diff usefulness
- approval queue clarity

### Manual review sets
Prepare fixed scenarios:
- long-running project
- conflicting guidance
- repeated missed commitment
- identity revision proposal with weak evidence
- high-risk boundary change

---

## 11. Biggest Delivery Risks

### Risk 1: Trying to build simulation too early
**Mitigation:** defer to Phase 6.

### Risk 2: Overcomplicated ontology
**Mitigation:** keep schemas flexible with JSON fields where needed.

### Risk 3: Retrieval quality disappoints
**Mitigation:** prioritize the context compiler and hybrid search, not just embeddings.

### Risk 4: Review burden too high
**Mitigation:** risk-based approval rules and batching.

### Risk 5: Self-model becomes too rigid
**Mitigation:** draft-first revisions, confidence labels, periodic re-review.

---

## 12. Recommended Cuts If Time Is Tight

Cut these first:
- simulation
- trust weighting sophistication
- advanced influence maps
- fully automated semantic promotion
- advanced analytics dashboards

Do **not** cut:
- provenance
- audit events
- version history
- resume bundle
- approval queue for meaningful revisions

---

## 13. Launch Criteria for MVP

Ship the MVP when all are true:

1. After a session break, the system can produce a useful resume bundle.
2. The agent can maintain threads/projects/commitments over time.
3. The system can store journal reflections and generate weekly synthesis.
4. A steward can inspect current self-model and compare to prior versions.
5. Revision proposals are visible and gated.
6. All durable updates are auditable.

---

## 14. Post-MVP Roadmap

### Next after MVP
- hybrid retrieval improvements
- contradiction management
- salience scoring
- drift alerts
- habits and recurring reviews

### Later
- simulation
- influence mapping
- richer relational guidance modeling
- deeper analytics
- multi-steward governance

---

## 15. Suggested 8–12 Week Delivery Plan

### Weeks 1–2
Foundations, schema, auth, audit, memory/project/thread basics

### Weeks 3–4
Resume bundle, memory search, project UI, commitments

### Weeks 5–6
Journal system, weekly synthesis, self-model storage

### Weeks 7–8
Diffing, revision proposals, steward views

### Weeks 9–10
Approvals, freeze controls, hardening, tests

### Weeks 11–12
Hybrid retrieval, polishing, pilot evaluation

---

## 16. Concrete MVP Definition

If you need a single sentence definition:

> The MVP is a governed continuity system that lets an agent remember important things, resume unfinished work, reflect over time, maintain a versioned self-model, and route meaningful self-revisions through human review.

---

## 17. Builder Recommendation

If you are building this now, the smartest sequence is:

1. get continuity working,
2. make it inspectable,
3. add reflection,
4. version the self-model,
5. only then add governance and higher-order revision logic.

That path gets you a real product faster and avoids premature complexity.
