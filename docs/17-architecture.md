# Architecture

This page provides a system-level walkthrough of all Engram components, data flows, and design decisions. It's intended for developers who want to understand the internals, contribute to the codebase, or build deep integrations.

---

## System Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   Agents/Users  │     │   CLI / SDK / TUI │     │    Playground UI    │
│                 │     │                   │     │   (Vite + React)    │
└────────┬────────┘     └────────┬──────────┘     └────────┬────────────┘
         │                       │                          │
         ▼                       ▼                          ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Gateway API (FastAPI)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐│
│  │   Auth   │ │  Registry│ │ Routing  │ │  Tasks   │ │ Federation  ││
│  │  Router  │ │  Router  │ │  Router  │ │  Router  │ │   Router    ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────────┘│
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐│
│  │Discovery │ │  Events  │ │  Traces  │ │ Evolution│ │   Memory    ││
│  │  Router  │ │  Router  │ │  Router  │ │  Router  │ │   Router    ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └─────────────┘│
└────────────────────────────┬───────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         Orchestrator                                   │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐               │
│  │ MCP Connector │ │ CLI Connector │ │ A2A Connector │  ...          │
│  └───────────────┘ └───────────────┘ └───────────────┘               │
└──────────────────────────┬─────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌──────────────────┐ ┌──────────┐ ┌──────────────┐
│  Semantic Layer  │ │   ML     │ │  Reliability │
│  (OWL + Mapper)  │ │  Layer   │ │  Middleware   │
└──────────────────┘ └──────────┘ └──────────────┘
              │            │            │
              ▼            ▼            ▼
┌──────────────────┐ ┌──────────┐ ┌──────────────┐
│  PostgreSQL /    │ │  Redis   │ │ Swarm Memory │
│  SQLite          │ │          │ │ (SQLite+Prolog)│
└──────────────────┘ └──────────┘ └──────────────┘
```

---

## Gateway API

The FastAPI application (`app/main.py`) is the central entrypoint:

### Lifespan Management

The FastAPI `lifespan` handler initializes and shuts down all services:

**Startup:**
1. Database engine and session factory creation
2. Table creation (`SQLModel.metadata.create_all`)
3. Alembic migration check
4. Orchestration service initialization
5. Background service startup (discovery, task worker, workflow scheduler, event listener)
6. Prometheus instrumentator setup
7. Sentry SDK initialization

**Shutdown:**
1. Background service cancellation
2. Database engine disposal
3. Redis connection cleanup

### Middleware Stack

Requests pass through this middleware pipeline (in order):

1. **CORS** — `CORSMiddleware` with configurable origins
2. **Security Headers** — Custom middleware injecting X-Content-Type-Options, X-Frame-Options, etc.
3. **HTTPS Redirect** — Redirects HTTP to HTTPS when `HTTPS_ONLY=true`
4. **Rate Limiting** — `slowapi` with `RATE_LIMIT_DEFAULT`
5. **Prometheus** — `prometheus-fastapi-instrumentator` for metrics at `/metrics`

---

## API Routers

The gateway registers 16+ router modules:

| Router | Prefix | Purpose |
|---|---|---|
| `auth` | `/auth` | Login, signup, EAT generation, token management |
| `endpoints` | `/api/v1/endpoints` | General API endpoints |
| `discovery` | `/api/v1/discovery` | Agent and tool discovery |
| `permissions` | `/api/v1/permissions` | Permission management |
| `credentials` | `/credentials` | Provider credential storage |
| `orchestration` | `/api/v1/orchestration` | Task orchestration and handoffs |
| `tasks` | `/tasks` | Task submission and status |
| `workflows` | `/api/v1/workflows` | Workflow scheduling and management |
| `registry` | `/api/v1/registry` | Tool registration (OpenAPI, CLI, manual) |
| `events` | `/events` | Event listeners and sync |
| `tracing` | `/api/v1/traces` | Semantic execution traces |
| `catalog` | `/api/v1/catalog` | Pre-optimized tool catalog |
| `reconciliation` | `/api/v1/reconciliation` | Self-healing status and triggers |
| `routing` | `/api/v1/routing` | Routing tests and stats |
| `evolution` | `/api/v1/evolution` | Self-evolving tool proposals |
| `federation` | `/api/v1/federation` | Protocol translation and handoffs |
| `memory` | `/api/v1/memory` | Swarm memory queries |

---

## Orchestrator & Connectors

The `Orchestrator` class coordinates all protocol operations:

- **Protocol detection** — Determines source and target protocols from request context
- **Connector dispatch** — Routes to the appropriate protocol connector
- **Execution tracking** — Creates trace records for every execution
- **Error handling** — Classifies errors and triggers appropriate recovery strategies

### IntentResolver

The `IntentResolver` translates natural-language requests into structured protocol payloads:

```
"send a notification about the deploy" → {"tool": "slack", "action": "send_message", "params": {"text": "..."}}
```

---

## Semantic Layer

### SemanticMapper

The core translation engine (`app/semantic/semantic_mapper.py`):

- **Field flattening** — Nested JSON to dot-notation paths
- **Ontology resolution** — `resolve_equivalent()` maps fields through OWL concepts
- **Bidirectional normalization** — Translates payloads in both directions

### OWL Ontology Management

Two ontologies power the semantic layer:

| Ontology | File | Content |
|---|---|---|
| `protocols.owl` | `app/semantic/protocols.owl` | Protocol concepts, field semantics, equivalence relations |
| `security.owl` | `app/semantic/security.owl` | Permission concepts, semantic scopes, access control |

Loaded via `rdflib` and `owlready2`, providing SPARQL queries and OWL reasoning.

### BidirectionalNormalizer

Handles forward and reverse translation through the ontology bridge.

### DynamicRuleSynthesizer

Uses the configured LLM to propose new mapping rules for novel field relationships not covered by the ontology.

### ProfileSemanticMapper

Extends the base mapper with user-profile-aware semantic resolution.

---

## ML Layer

### ml_mapper.py

The ML-based field mapping model:

- **Algorithm** — scikit-learn pipeline (TF-IDF vectorizer + classifier)
- **Training data** — Labeled field mappings from successful executions
- **Model storage** — Serialized to `ML_MODEL_PATH` via `joblib`
- **Auto-retraining** — Triggered after `ML_AUTO_RETRAIN_THRESHOLD` corrections

### train_mapping_model.py

Standalone training script for the mapping model. Can be run periodically or triggered by the evolution pipeline.

---

## Routing Engine

The `tool_routing.py` module implements weighted composite routing:

1. **Embedding generation** — `sentence-transformers` converts task descriptions to vectors
2. **Candidate scoring** — Each tool/backend pair gets a composite score
3. **Caching** — Redis-backed cache with `ROUTING_CACHE_TTL_SECONDS`
4. **Context pruning** — Budget-based token limit pruning
5. **Selection** — Highest-scoring candidate is chosen (or parallel if below confidence gap)

---

## Reliability Middleware

The `reliability/middleware.py` wraps all routing calls with:

- **Circuit breaker** — Per-destination failure tracking with automatic cooldown
- **Retry with exponential backoff** — Via `tenacity` library
- **Idempotency** — SHA-256 payload hash + correlation ID for exactly-once semantics
- **Schema inference** — Dynamic Pydantic model creation and validation
- **TUI trace logging** — Real-time events for circuit breaker trips, retries, and failures

See [Reliability Middleware](./18-reliability-middleware.md) for full details.

---

## Swarm Memory

The `bridge/memory.py` module provides persistent semantic fact storage:

| Layer | Technology | Purpose |
|---|---|---|
| **Storage** | SQLite | Durable fact persistence |
| **Reasoning** | SWI-Prolog (`pyswip`) | Semantic inference, conflict detection |
| **Rules** | pyDatalog | Declarative conflict resolution |
| **Normalization** | SemanticMapper | Ontology-backed concept alignment |

---

## Task Queue

SQL-backed task queue with lease-based processing:

| Component | Configuration |
|---|---|
| **Poll interval** | `TASK_POLL_INTERVAL_SECONDS` (2.0s) |
| **Lease duration** | `TASK_LEASE_SECONDS` (60s) |
| **Max attempts** | `TASK_MAX_ATTEMPTS` (5) |
| **Evolution tasks** | Celery for async ML jobs |

### Workflow Scheduler

Periodic workflow execution:
- **Poll interval** — `WORKFLOW_SCHEDULER_POLL_SECONDS` (5.0s)
- **Batch size** — `WORKFLOW_SCHEDULER_BATCH_SIZE` (20)

---

## Event System

Redis Streams-based event pipeline:

- **Stream key** — `engram:events`
- **Consumer group** — `engram-event-workers`
- **Fallback** — Polling listener when Redis is unavailable
- **TUI integration** — Events routed to trace panels via `tui_bridge.py`

---

## Database Layer

| Technology | Use Case |
|---|---|
| **SQLAlchemy + SQLModel** | ORM and schema definitions |
| **asyncpg** | Async PostgreSQL driver (production) |
| **aiosqlite** | Async SQLite driver (local dev) |
| **Alembic** | Schema migrations |

### Smart Fallback

The `_finalize_database_url` validator in `Settings` automatically detects the runtime environment and switches between PostgreSQL and SQLite.

---

## Background Services

All auto-started via FastAPI lifespan:

| Service | Purpose |
|---|---|
| **Discovery Service** | Periodic agent and tool health checks |
| **Task Worker** | Polls and processes queued tasks |
| **Workflow Scheduler** | Triggers scheduled workflows |
| **Event Listener** | Processes Redis Stream events |

---

## Security Architecture

| Layer | Mechanism |
|---|---|
| **Authentication** | JWT validation (HS256/RS256) |
| **Authorization** | EAT semantic scopes from `security.owl` |
| **Fail-closed** | Security checks deny when infrastructure is down |
| **Credential encryption** | Fernet symmetric encryption |
| **Transport security** | HTTPS redirect, security headers, CORS |
| **Rate limiting** | Per-IP with `slowapi` |

---

## What's Next

- **[Reliability Middleware](./18-reliability-middleware.md)** — Deep dive into the reliability layer
- **[Contributing](./19-contributing.md)** — Development setup and contribution guidelines
- **[SDK & Python Library](./16-sdk-python-library.md)** — Programmatic integration
