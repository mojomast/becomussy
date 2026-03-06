# becomussy

A governed continuity system for agent self-development.

## Overview

becomussy is a platform that enables an AI agent to:

- **Remember** important things across sessions with structured multi-layer memory
- **Resume** unfinished work through active threads, projects, and commitments
- **Reflect** over time through a journal system and periodic synthesis
- **Maintain** a versioned self-model with structured semantic diffing
- **Route** meaningful self-revisions through human review and governance

Every durable update is auditable. High-risk identity changes require human approval. The system is designed to be inspectable from day one.

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (for PostgreSQL and Redis)
- **Python 3.12+**
- **Node.js 20+** (for the frontend)

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/mojomast/becomussy.git
   cd becomussy
   ```

2. **Copy environment config**

   ```bash
   cp .env.example .env
   ```

3. **Start infrastructure** (PostgreSQL with pgvector, Redis)

   ```bash
   docker compose -f infrastructure/docker-compose.yml up -d db redis
   ```

4. **Set up the backend**

   ```bash
   cd backend

   # Create a virtual environment (recommended)
   python -m venv .venv && source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Run database migrations
   alembic upgrade head

   # (Optional) Seed demo data
   python -m scripts.seed_data

   # Start the API server
   uvicorn app.main:app --reload --port 8000
   ```

5. **Set up the frontend**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Open the app**

   - Frontend: [http://localhost:3000](http://localhost:3000)
   - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Full Docker Compose

To run everything in Docker:

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

## API Documentation

FastAPI auto-generates interactive API docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### API Endpoints Summary

| Endpoint                              | Method | Description                              |
|---------------------------------------|--------|------------------------------------------|
| `/api/v1/health`                      | GET    | Health check                             |
| **Memory**                            |        |                                          |
| `/api/v1/memory`                      | POST   | Create a memory item                     |
| `/api/v1/memory/search`               | GET    | Search memory items                      |
| `/api/v1/memory/{id}`                 | GET    | Get a memory item                        |
| `/api/v1/memory/{id}`                 | PATCH  | Update a memory item                     |
| `/api/v1/memory/{id}/reinforce`       | POST   | Reinforce a memory (bump salience)       |
| `/api/v1/memory/{id}/contradict`      | POST   | Record a contradiction                   |
| **Threads**                           |        |                                          |
| `/api/v1/threads`                     | POST   | Create a thread                          |
| `/api/v1/threads`                     | GET    | List threads                             |
| `/api/v1/threads/{id}`               | GET    | Get a thread                             |
| `/api/v1/threads/{id}`               | PATCH  | Update a thread                          |
| **Projects**                          |        |                                          |
| `/api/v1/projects`                    | POST   | Create a project                         |
| `/api/v1/projects`                    | GET    | List projects                            |
| `/api/v1/projects/{id}`              | GET    | Get a project                            |
| `/api/v1/projects/{id}`              | PATCH  | Update a project                         |
| `/api/v1/projects/{id}/commitments`  | POST   | Create a commitment for a project        |
| `/api/v1/projects/{id}/commitments`  | GET    | List commitments for a project           |
| **Commitments**                       |        |                                          |
| `/api/v1/commitments`                 | POST   | Create a commitment                      |
| `/api/v1/commitments`                 | GET    | List all commitments                     |
| `/api/v1/commitments/{id}`           | GET    | Get a commitment                         |
| `/api/v1/commitments/{id}`           | PATCH  | Update a commitment                      |
| **Journal**                           |        |                                          |
| `/api/v1/journal`                     | POST   | Create a journal entry                   |
| `/api/v1/journal/search`              | GET    | Search journal entries                   |
| `/api/v1/journal/{id}`              | GET    | Get a journal entry                      |
| `/api/v1/journal/{id}`              | PATCH  | Update a journal entry                   |
| `/api/v1/journal/summarize`           | POST   | Summarize entries in a date range        |
| **Self-Model**                        |        |                                          |
| `/api/v1/self-model/current`          | GET    | Get current self-model version           |
| `/api/v1/self-model/history`          | GET    | Get version history                      |
| `/api/v1/self-model/version/{id}`    | GET    | Get a specific version                   |
| `/api/v1/self-model/version`          | POST   | Create a new version                     |
| `/api/v1/self-model/diff`             | POST   | Compute diff between two versions        |
| `/api/v1/self-model/revision-proposal`| POST  | Create a revision proposal               |
| **Approvals / Governance**            |        |                                          |
| `/api/v1/approvals/pending`           | GET    | List pending approvals                   |
| `/api/v1/approvals/{id}/approve`     | POST   | Approve a revision proposal              |
| `/api/v1/approvals/{id}/reject`      | POST   | Reject a revision proposal               |
| `/api/v1/approvals/{id}/defer`       | POST   | Defer for more evidence                  |
| `/api/v1/approvals/policy/check`      | GET    | Check governance policy                  |
| `/api/v1/approvals/freeze`            | GET    | Get freeze status                        |
| `/api/v1/approvals/freeze`            | POST   | Set emergency freeze                     |
| **Continuity**                        |        |                                          |
| `/api/v1/continuity/resume`           | GET    | Get resume bundle                        |
| `/api/v1/continuity/resume/debug`     | GET    | Get resume bundle with debug info        |
| **Audit**                             |        |                                          |
| `/api/v1/audit`                       | GET    | List audit events                        |
| `/api/v1/audit/{id}`                 | GET    | Get a single audit event                 |

### Authentication (MVP)

The MVP uses header-based auth. Include these headers with every request:

```
X-User-Id: your-user-id
X-User-Role: steward
```

Valid roles: `agent_runtime`, `steward`, `reviewer`, `admin`, `observer`

## Architecture

The system follows a **modular monolith** pattern. All services live in a single FastAPI application but maintain clean internal boundaries.

```
backend/
  app/
    api/v1/           # HTTP route handlers
    core/             # Config, security
    db/               # Database engine, session, base models
    models/           # SQLAlchemy ORM models
    schemas/          # Pydantic request/response schemas
    services/         # Business logic (one module per domain)
      memory/         # Memory CRUD, search, reinforce, contradict
      threads/        # Thread CRUD and listing
      projects/       # Project & commitment CRUD
      journal/        # Journal entry CRUD, search, summarize
      self_model/     # Self-model versions, diff engine
      revisions/      # Revision proposals, risk classification
      governance/     # Approvals, policy checks, freeze controls
      search/         # Context compiler, keyword search
      audit/          # Audit event logging
    workers/          # Background job definitions (future)
  migrations/         # Alembic database migrations
  tests/
    unit/             # Pure unit tests (no DB required)
    integration/      # API integration tests (requires PostgreSQL)
  scripts/
    seed_data.py      # Demo data seeder
```

## Development

### Running Tests

Tests require a running PostgreSQL instance. Start it with Docker Compose:

```bash
docker compose -f infrastructure/docker-compose.yml up -d db
```

Create the test database:

```bash
docker compose -f infrastructure/docker-compose.yml exec db \
  psql -U becoming -c "CREATE DATABASE becoming_test;"
```

Run the tests:

```bash
cd backend

# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With verbose output
pytest -v
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "describe your change"

# Apply all migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Show current migration
alembic current
```

### Seed Data

```bash
cd backend
python -m scripts.seed_data
```

This creates demo memories, threads, projects, commitments, journal entries, a self-model version, and a pending revision proposal.

## Key Concepts

- **Memory Items**: Multi-layer memory (episodic, semantic, working, relational, autobiographical) with provenance tracking
- **Threads**: Active concerns or topics being tracked
- **Projects**: Structured initiatives with milestones and commitments
- **Commitments**: Explicit promises with due dates and risk tracking
- **Journal Entries**: Reflections, observations, and synthesis artifacts
- **Self-Model Versions**: Versioned snapshots of the agent's self-understanding across 4 facets (descriptive, aspirational, constrained, relational)
- **Revision Proposals**: Evidence-linked proposals for identity changes, gated by risk-based governance
- **Resume Bundle**: A compiled continuity snapshot assembled at session start
- **Audit Events**: Immutable log of every durable change in the system
