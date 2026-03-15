# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Run locally
```bash
uvicorn app.main:app --reload
```
Swagger UI is available at `http://localhost:8000/docs`.

### Run with Docker (recommended — starts app + PostgreSQL + Redis + Prometheus + Grafana)
```bash
docker compose up --build
```

### Run staging environment (adds WireMock for external agent mocking)
```bash
docker compose -f docker-compose.staging.yml up --build -d
```

### Install dependencies
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Run tests
```bash
pytest -q
```

Run a single test file:
```bash
pytest tests/test_api_endpoints.py -q
```

Run with coverage:
```bash
pytest --cov=app tests/
```

Integration tests require live services and are marked; skip them by default:
```bash
pytest -q -m "not integration"
```

Run the full E2E integration flow (starts a local server internally):
```bash
$env:PYTHONPATH="."
python tests/integration/run_integration_e2e.py
```

### Generate a JWT for local testing
```bash
python scripts/generate_token.py --secret <AUTH_JWT_SECRET> --scope translate:a2a
```
This mints an HS256 token matching the `AUTH_ISSUER`/`AUTH_AUDIENCE`/`AUTH_JWT_SECRET` values in `.env`.

---

## Architecture

### Overview

The service is a **FastAPI** app (`app/main.py`) that acts as a universal bridge between AI agents that speak different protocols (A2A, MCP, ACP). On startup it initializes the database, starts a background `DiscoveryService` (health-pings registered agents), and starts a background `TaskWorker` (processes queued translation tasks).

### Translation pipeline

A translation request flows through three layers:

1. **`TranslatorEngine`** (`app/core/translator.py`) — handles the structural/envelope transformation. Each registered `(source, target)` protocol pair maps to a dedicated method (e.g., `_translate_a2a_to_mcp`). Before translating, it applies **version delta upgrades** loaded from the `ProtocolVersionDelta` DB table to normalize the source message to the expected version. Delta rules support `rename`, `drop`, and `set` operations on dotted-path keys.

2. **`Orchestrator` + `ProtocolGraph`** (`app/messaging/orchestrator.py`) — wraps `TranslatorEngine` with multi-hop routing. Protocols are nodes and each registered translator pair is a directed edge. `nx.shortest_path` (Dijkstra by weight) determines the optimal chain (e.g., A2A → MCP → ACP when no direct A2A → ACP translator exists). Each hop is executed sequentially; a `HandoffResult` records the route and per-hop snapshots.

3. **`SemanticMapper`** (`app/semantic/mapper.py`) — resolves the **content/meaning** of payload fields. It uses:
   - OWL ontologies via `owlready2` (the bundled `app/semantic/protocols.owl` covers A2A/MCP/ACP namespaces).
   - `PyDatalog` rule engine for explicit field renames (e.g., `user_info.name → profile.fullname`).
   - Redis cache for repeated concept lookups (key pattern `semantic:equivalent:<protocol>:<concept>`).
   - The `DataSiloResolver` method first validates against JSON Schema, flattens nested dicts, applies PyDatalog rules, then falls back to ontology lookups.

### ML fallback mapping

When a translation fails (usually a semantic mapping gap), `app/services/mapping_failures.py` logs the failure to `MappingFailureLog` and calls `app/semantic/ml_mapper.py`. `MappingPredictor` uses a TF-IDF + Logistic Regression sklearn pipeline trained on `ProtocolMapping.semantic_equivalents` entries stored in the DB. Predictions above `ML_AUTO_APPLY_THRESHOLD` (default 0.85) are auto-applied; others are surfaced as `mapping_suggestions` in the `BetaTranslateResponse`. The model is persisted to `app/semantic/models/mapping_model.joblib`.

### Task queue

`POST /api/v1/queue/enqueue` persists a `Task` row (JSONB payload, protocol pair, target agent UUID) to PostgreSQL. The `TaskWorker` background loop polls with a lease (`TASK_POLL_INTERVAL_SECONDS`, `TASK_LEASE_SECONDS`) and calls `Orchestrator.handoff`. On success it creates an `AgentMessage` row for the target agent. On failure it retries up to `TASK_MAX_ATTEMPTS`; exhausted tasks move to `DEAD_LETTER` status. Target agents poll `POST /api/v1/agents/{agent_id}/messages/poll` and acknowledge via `POST /api/v1/agents/messages/{message_id}/ack`.

### Agent registry & discovery

`DiscoveryService` (`app/services/discovery.py`) pings each registered agent's `/health` endpoint every 60 s to update `is_active` in the `AgentRegistry` table. `find_collaborators` scores candidates using:

```
score = (shared_protocols + mappable_protocols) / total_candidate_protocols
```

where `mappable_protocols` are protocols the candidate supports that can be reached from the requester's protocols via `ProtocolMapping` rows in the DB.

### Authentication

All `/api/v1` routes require a `Bearer` JWT (`app/core/security.py`). The token must carry `iss`, `aud`, and `exp` claims matching `AUTH_ISSUER`, `AUTH_AUDIENCE`. Scopes `translate:a2a` and `translate:beta` gate the respective endpoints. For HS256 the shared secret is `AUTH_JWT_SECRET`; for RS*/ES* set `AUTH_JWT_PUBLIC_KEY`.

### Configuration

All settings are in `app/core/config.py` via `pydantic-settings` and read from environment variables / `.env`. Notable non-obvious defaults:
- `DATABASE_URL` defaults to `postgresql+asyncpg://admin:password@db/translator_db` (the Docker Compose service name `db`).
- `REDIS_ENABLED=true` — set to `false` to disable semantic caching (the mapper degrades gracefully).
- `REDIS_HOST` defaults to `redis` (Docker Compose service name).
- `HTTPS_ONLY=false` — set to `true` to enable `HTTPSRedirectMiddleware`.

### Observability

- **Structured logging**: `structlog` configured in `app/core/logging.py`.
- **Prometheus metrics**: exposed at `GET /metrics` via `prometheus-fastapi-instrumentator`; translation success/error counters are recorded in `app/core/metrics.py`.
- **Sentry**: initialized at startup when `SENTRY_DSN` is set.
- **Grafana dashboard**: provisioned automatically from `monitoring/grafana/`.

### Database

SQLModel + asyncpg on PostgreSQL (Neon-compatible). `init_db()` auto-creates tables via `SQLModel.metadata.create_all` and migrates `TIMESTAMP` columns to `TIMESTAMPTZ` if needed. There is no Alembic — schema changes must be handled manually or by dropping/recreating tables in development.

### Test layout

- `tests/` — unit tests (no external services required).
- `tests/integration/` — end-to-end flows (`@pytest.mark.integration`), require live services.
- `tests/wiremock/` — WireMock stub mappings for staging.
- `conftest.py` at root adds the project root to `sys.path`.
- All async tests use `@pytest.mark.asyncio`.
