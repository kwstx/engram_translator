# Configuration

Engram's configuration system spans three layers — a YAML config file, environment variables, and a backend settings model — unified by a smart precedence chain that adapts to your runtime environment automatically.

---

## Config File Location

```
~/.engram/config.yaml
```

Created by `engram init`. This file stores CLI-level preferences that affect how the `engram` command behaves. It is separate from the backend's `app/core/config.py` settings, which are configured via environment variables or `.env` files.

---

## Config File Format

```yaml
# ~/.engram/config.yaml
api_url: http://127.0.0.1:8000
backend_preference: mcp
model_provider: openai
verbose: false
```

### CLI Configuration Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `api_url` | `str` | `http://127.0.0.1:8000` | Base URL for the Engram API. Change this when connecting to a remote gateway. |
| `backend_preference` | `enum` | `mcp` | Default backend for tool execution: `mcp` (structured reliability) or `cli` (speed). |
| `model_provider` | `str` | `openai` | Default AI model provider for semantic operations. |
| `verbose` | `bool` | `false` | Enable verbose logging for debugging. Shows keyring warnings and detailed error context. |

Modify via CLI:

```bash
engram config set api_url http://my-server:8000
engram config set backend_preference cli
engram config set model_provider anthropic
engram config show   # Verify changes
```

---

## Backend Settings Reference

The backend settings are defined in `app/core/config.py` as a Pydantic `BaseSettings` model. These are configured via environment variables or a `.env` file at the project root. The backend also loads `~/.engram/config.yaml` at startup as a secondary source (environment variables take precedence).

### Core Runtime

| Variable | Type | Default | Description |
|---|---|---|---|
| `PROJECT_NAME` | `str` | `Agent Translator Middleware` | Application name for logging and metadata |
| `API_V1_STR` | `str` | `/api/v1` | API version prefix for all routes |
| `ENVIRONMENT` | `str` | `development` | Runtime environment: `development`, `staging`, `production` |
| `LOG_LEVEL` | `str` | `INFO` | Application log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `MODEL_PROVIDER` | `str` | `openai` | Default LLM provider |
| `BASE_URL` | `str` | `http://127.0.0.1:8000` | Base URL for self-referencing |
| `DEFAULT_PERSONALITY` | `str` | `optimistic` | Default personality for agent responses |

### Provider API Keys

| Variable | Type | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | `str` | — | Anthropic (Claude) API key |
| `PERPLEXITY_API_KEY` | `str` | — | Perplexity API key |
| `SLACK_API_TOKEN` | `str` | — | Slack OAuth token |
| `X_BEARER_TOKEN` | `str` | — | X (Twitter) bearer token |

### Routing Configuration

The routing engine uses a weighted composite score to choose the best tool and backend for each task. These weights control the relative importance of each factor:

| Variable | Type | Default | Description |
|---|---|---|---|
| `ROUTING_EMBEDDING_MODEL` | `str` | `all-MiniLM-L6-v2` | Sentence-transformer model for semantic matching |
| `ROUTING_STATS_WINDOW_HOURS` | `int` | `168` | Rolling window for performance stats (7 days) |
| `ROUTING_CACHE_TTL_SECONDS` | `int` | `60` | Redis cache TTL for routing decisions |
| `ROUTING_WEIGHT_SIMILARITY` | `float` | `0.55` | Weight for semantic similarity score |
| `ROUTING_WEIGHT_SUCCESS` | `float` | `0.20` | Weight for historical success rate |
| `ROUTING_WEIGHT_LATENCY` | `float` | `0.15` | Weight for latency score |
| `ROUTING_WEIGHT_TOKEN_COST` | `float` | `0.07` | Weight for token efficiency |
| `ROUTING_WEIGHT_CONTEXT_OVERHEAD` | `float` | `0.03` | Weight for context overhead |
| `ROUTING_WEIGHT_PREFERENCE` | `float` | `0.10` | Weight for user's backend preference |
| `ROUTING_WEIGHT_PREDICTIVE` | `float` | `0.15` | Weight for predictive optimization |
| `ROUTING_BUDGET_TOKEN_LIMIT` | `int` | `8000` | Maximum token budget for routing |
| `ROUTING_PARALLEL_CONFIDENCE_THRESHOLD` | `float` | `0.05` | Minimum score gap to avoid parallel execution |

#### Tuning Routing Weights

The weights should sum to approximately 1.0 (minor deviations are acceptable). Adjust them based on your workload priorities:

| Priority | Recommended Tuning |
|---|---|
| **Accuracy first** | Increase `ROUTING_WEIGHT_SIMILARITY` to 0.7, decrease `ROUTING_WEIGHT_LATENCY` to 0.05 |
| **Speed first** | Increase `ROUTING_WEIGHT_LATENCY` to 0.3, decrease `ROUTING_WEIGHT_SIMILARITY` to 0.3 |
| **Cost optimization** | Increase `ROUTING_WEIGHT_TOKEN_COST` to 0.2, decrease `ROUTING_WEIGHT_PREDICTIVE` to 0.05 |
| **Reliability first** | Increase `ROUTING_WEIGHT_SUCCESS` to 0.35, decrease others proportionally |

### ML Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `ML_ENABLED` | `bool` | `true` | Enable/disable ML-based mapping suggestions |
| `ML_MODEL_PATH` | `str` | `app/semantic/models/mapping_model.joblib` | Path to the trained mapping model |
| `ML_MIN_TRAIN_SAMPLES` | `int` | `20` | Minimum samples before training the ML model |
| `ML_AUTO_APPLY_THRESHOLD` | `float` | `0.85` | Confidence threshold for auto-applying ML suggestions |
| `ML_AUTO_RETRAIN_THRESHOLD` | `int` | `5` | Number of manual corrections before auto-retraining |
| `MAPPING_FAILURE_MAX_FIELDS` | `int` | `50` | Maximum fields to analyze on mapping failure |
| `MAPPING_FAILURE_PAYLOAD_MAX_KEYS` | `int` | `50` | Maximum payload keys to include in failure analysis |

### Database Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | `str` | Auto-generated | Full database connection URL (auto-built from Postgres settings) |
| `POSTGRES_SERVER` | `str` | `db` | PostgreSQL server hostname |
| `POSTGRES_USER` | `str` | `admin` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `str` | `password` | PostgreSQL password |
| `POSTGRES_DB` | `str` | `translator_db` | Database name |

> **Important:** The default `POSTGRES_SERVER` is `db`, which resolves inside Docker Compose. For local development, the smart fallback automatically switches to SQLite (`./engram.db`). For production, set `DATABASE_URL` explicitly to your managed PostgreSQL instance.

#### Database URL Processing

Engram performs automatic URL processing to ensure compatibility:

1. `postgres://` → `postgresql+asyncpg://` (asyncpg compatibility)
2. `sslmode=require` → `ssl=true` (asyncpg doesn't accept `sslmode`)
3. Strips incompatible parameters: `channel_binding`, `sslrootcert`, `sslcert`, `sslkey`, `sslcrl`

### Redis Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `REDIS_ENABLED` | `bool` | `true` | Enable/disable Redis integration |
| `REDIS_HOST` | `str` | `redis` | Redis server hostname |
| `REDIS_PORT` | `int` | `6379` | Redis port |
| `REDIS_DB` | `int` | `0` | Redis database number |
| `REDIS_PASSWORD` | `str` | — | Redis password (optional) |
| `REDIS_URL` | `str` | Auto-generated | Full Redis connection URL |
| `REDIS_CONNECT_TIMEOUT_SECONDS` | `float` | `0.2` | Connection timeout |
| `REDIS_SOCKET_TIMEOUT_SECONDS` | `float` | `0.2` | Socket timeout |
| `SEMANTIC_CACHE_TTL_SECONDS` | `int` | `600` | Cache TTL for semantic operations (10 minutes) |

> **Note:** Redis is optional for local development. When `REDIS_HOST` is `redis` (Docker default) and no Docker environment is detected, Redis is auto-disabled. All Redis-dependent features gracefully degrade.

### Event Stream Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `EVENT_STREAM_KEY` | `str` | `engram:events` | Redis Stream key for events |
| `EVENT_STREAM_GROUP` | `str` | `engram-event-workers` | Consumer group name |
| `EVENT_STREAM_CONSUMER` | `str` | `worker-1` | Consumer name within the group |
| `EVENT_STREAM_BLOCK_MS` | `int` | `2000` | Read block timeout in milliseconds |
| `EVENT_STREAM_BATCH` | `int` | `25` | Number of events to read per batch |
| `EVENT_STREAM_MAXLEN` | `int` | `10000` | Maximum stream length (older events trimmed) |
| `EVENT_POLL_INTERVAL_SECONDS` | `float` | `10.0` | Fallback polling interval when Redis Streams unavailable |

### Security Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `AUTH_ISSUER` | `str` | `https://auth.example.com/` | JWT issuer claim |
| `AUTH_AUDIENCE` | `str` | `translator-middleware` | JWT audience claim |
| `AUTH_JWT_ALGORITHM` | `str` | `HS256` | JWT signing algorithm |
| `AUTH_JWT_SECRET` | `str` | — | JWT signing secret (required for production) |
| `AUTH_JWT_PUBLIC_KEY` | `str` | — | JWT public key (for RS256/ES256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `10080` | Session token lifetime (7 days) |
| `EAT_ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `15` | EAT access token lifetime (15 minutes) |
| `EAT_REFRESH_TOKEN_EXPIRE_MINUTES` | `int` | `10080` | EAT refresh token lifetime (7 days) |
| `PROVIDER_CREDENTIALS_ENCRYPTION_KEY` | `str` | — | Fernet key for encrypting stored provider credentials |
| `AUTH_FAIL_CLOSED` | `bool` | `true` | Deny access when Redis is down (fail-closed security) |
| `SEMANTIC_AUTH_FAIL_CLOSED` | `bool` | `true` | Deny access when semantic scope check fails |
| `HTTPS_ONLY` | `bool` | `false` | Force HTTPS redirect in production |
| `CORS_ORIGINS` | `list` | `["*"]` | Allowed CORS origins |
| `RATE_LIMIT_DEFAULT` | `str` | `100/minute` | Default API rate limit |
| `RATE_LIMIT_ENABLED` | `bool` | `true` | Enable/disable rate limiting |
| `SANDBOX_ENABLED` | `bool` | `true` | Enable sandbox mode for playground |

### Ontology Paths

| Variable | Type | Default | Description |
|---|---|---|---|
| `DEFAULT_ONTOLOGY_PATH` | `str` | `app/semantic/protocols.owl` | Path to the protocol ontology |
| `SEMANTIC_SCOPE_ONTOLOGY_PATH` | `str` | `app/semantic/security.owl` | Path to the security scope ontology |

### Task Queue Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `TASK_POLL_INTERVAL_SECONDS` | `float` | `2.0` | How often the task worker checks for new tasks |
| `TASK_LEASE_SECONDS` | `int` | `60` | How long a task is leased to a worker before it's considered stale |
| `TASK_MAX_ATTEMPTS` | `int` | `5` | Maximum retry attempts for a failed task |
| `AGENT_MESSAGE_LEASE_SECONDS` | `int` | `60` | Lease duration for agent messages |
| `AGENT_MESSAGE_MAX_ATTEMPTS` | `int` | `5` | Maximum retry attempts for agent messages |

### Workflow Scheduler Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `WORKFLOW_SCHEDULER_POLL_SECONDS` | `float` | `5.0` | Polling interval for scheduled workflows |
| `WORKFLOW_SCHEDULER_BATCH_SIZE` | `int` | `20` | Number of workflows to process per batch |

### Trading Templates

| Variable | Type | Default | Description |
|---|---|---|---|
| `TRADING_TEMPLATES_ENABLED` | `bool` | `true` | Enable trading template integrations |
| `BINANCE_API_KEY` | `str` | — | Binance exchange API key |
| `BINANCE_SECRET` | `str` | — | Binance exchange API secret |
| `COINBASE_API_KEY` | `str` | — | Coinbase API key |
| `COINBASE_SECRET` | `str` | — | Coinbase API secret |
| `KALSHI_API_KEY` | `str` | — | Kalshi prediction market API key |
| `KALSHI_SECRET` | `str` | — | Kalshi API secret |
| `ROBINHOOD_API_KEY` | `str` | — | Robinhood API key |
| `ROBINHOOD_SECRET` | `str` | — | Robinhood API secret |
| `STRIPE_SECRET_KEY` | `str` | — | Stripe secret key |
| `PAYPAL_CLIENT_ID` | `str` | — | PayPal client ID |
| `PAYPAL_SECRET` | `str` | — | PayPal client secret |
| `FRED_API_KEY` | `str` | — | Federal Reserve Economic Data API key |
| `REUTERS_APP_KEY` | `str` | — | Reuters data API key |
| `BLOOMBERG_SERVICE_ID` | `str` | — | Bloomberg terminal service ID |

### Local LLM (Ollama)

| Variable | Type | Default | Description |
|---|---|---|---|
| `OLLAMA_BASE_URL` | `str` | `http://localhost:11434` | Ollama server base URL |
| `OLLAMA_MODEL` | `str` | `llama3.2` | Default Ollama model |

### Miscellaneous

| Variable | Type | Default | Description |
|---|---|---|---|
| `SENTRY_DSN` | `str` | — | Sentry error tracking DSN |
| `PYTHON_INTERPRETER` | `str` | `python` | Python interpreter path for CLI tool execution |

---

## Precedence & Smart Fallback

Configuration values are resolved in this order (highest priority first):

1. **Environment variables** — `ANTHROPIC_API_KEY=sk-ant-...` in your shell or `.env` file
2. **`~/.engram/config.yaml`** — Loaded by the `@model_validator(mode="before")` hook in `Settings`
3. **Defaults** — Hardcoded defaults in the `Settings` class

### Smart Fallback Logic

At startup, Engram detects whether it's running inside Docker/Kubernetes or locally:

```python
# From app/core/config.py
if not os.path.exists("/.dockerenv") and not os.environ.get("KUBERNETES_PORT"):
    # Not in Docker or K8s — switch to local-friendly defaults
    if "db:5432" in DATABASE_URL or POSTGRES_SERVER == "db":
        DATABASE_URL = "sqlite+aiosqlite:///./engram.db"
    if REDIS_HOST == "redis":
        REDIS_ENABLED = False
```

This means you never need to install PostgreSQL or Redis for local development. The detection is automatic and zero-configuration.

| Detected Environment | Database | Redis |
|---|---|---|
| Docker (`/.dockerenv` exists) | PostgreSQL via `db:5432` | Redis via `redis:6379` |
| Kubernetes (`KUBERNETES_PORT` set) | PostgreSQL via configured URL | Redis via configured URL |
| Local development (neither) | SQLite (`./engram.db`) | Disabled (in-memory fallback) |

---

## What's Next

- **[CLI Reference](./06-cli-reference.md)** — Every command, flag, and output format
- **[Docker & Kubernetes Setup](./03-docker-kubernetes.md)** — Deploy with the right environment variables
- **[EAT Identity & Security](./12-eat-identity-security.md)** — Configure authentication and authorization
- **[Observability & Tracing](./14-observability-tracing.md)** — Tune monitoring and alerting
