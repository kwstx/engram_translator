# Docker & Kubernetes Setup

Engram ships with production-ready Docker Compose and Kubernetes configurations. Docker Compose is ideal for single-server deployments and development environments. Kubernetes (via the included manifests) is designed for multi-node production workloads with horizontal scaling.

---

## Deployment Options

| Deployment | Who it's for | What you get |
|---|---|---|
| **Docker Compose** | Single-server, dev, staging | Full stack with one command — app, Postgres, Redis, Prometheus, Grafana |
| **Docker Compose (Staging)** | Pre-production validation | Stripped-down stack with production-like settings |
| **Kubernetes** | Production at scale | Declarative manifests with autoscaling, health checks, and observability |

---

## Docker Compose Quick Start

```bash
# Clone the repo
git clone https://github.com/kwstx/engram_translator.git
cd engram_translator

# Copy environment template
cp .env.example .env
# Edit .env with your API keys and secrets

# Start the full stack
docker compose up -d
```

This starts six services:

| Service | Port | Purpose |
|---|---|---|
| `app` | 8000 | Engram gateway API (FastAPI + Uvicorn) |
| `frontend` | 3000 | Playground UI (Vite + React) |
| `db` | 5432 | PostgreSQL 16 (persistent data) |
| `redis` | 6379 | Event streams, semantic caching, rate limiting |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3001 | Dashboards and alerting |

The app service hot-reloads on code changes (source volumes are mounted in development mode). For production, remove the volume mount and use the pre-built image.

### Verify the Stack

```bash
# Check all services are running
docker compose ps

# Test the gateway
curl http://localhost:8000/health

# View application logs
docker compose logs -f app

# Access the API docs
open http://localhost:8000/docs    # or xdg-open on Linux
```

---

## Environment Variables

The `.env` file at the project root is loaded by both Docker Compose and the application. Key variables:

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_USER` | `admin` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `password` | PostgreSQL password (**change in production!**) |
| `POSTGRES_DB` | `translator_db` | Database name |
| `REDIS_HOST` | `redis` | Redis hostname (use `redis` for Docker, `localhost` for local dev) |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_PASSWORD` | — | Redis password (optional, recommended for production) |
| `MODEL_PROVIDER` | `openai` | Default LLM provider for semantic operations |
| `ANTHROPIC_API_KEY` | — | API key for Claude-powered semantic reasoning |
| `PERPLEXITY_API_KEY` | — | API key for Perplexity search agent |
| `SLACK_API_TOKEN` | — | Slack OAuth token for messaging integration |
| `SENTRY_DSN` | — | Optional Sentry error tracking endpoint |
| `HTTPS_ONLY` | `false` | Force HTTPS redirect (set `true` in production) |
| `RATE_LIMIT_DEFAULT` | `100/minute` | Default API rate limit |
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |
| `AUTH_JWT_SECRET` | — | JWT signing secret (auto-generated if not set) |
| `PROVIDER_CREDENTIALS_ENCRYPTION_KEY` | — | Fernet key for encrypting stored credentials |
| `LOG_LEVEL` | `INFO` | Application log level |
| `ENVIRONMENT` | `development` | Environment name (`development`, `staging`, `production`) |

> **Warning:** Never commit `.env` to version control. The `.gitignore` excludes it by default. For Kubernetes deployments, use Secrets objects instead.

### Example `.env` for Production

```bash
# .env (production)
ENVIRONMENT=production
HTTPS_ONLY=true
POSTGRES_USER=engram_prod
POSTGRES_PASSWORD=<strong-random-password>
POSTGRES_DB=engram_production
REDIS_HOST=redis
REDIS_PASSWORD=<redis-password>
AUTH_JWT_SECRET=<64-char-random-string>
PROVIDER_CREDENTIALS_ENCRYPTION_KEY=<fernet-key>
ANTHROPIC_API_KEY=sk-ant-...
SENTRY_DSN=https://...@sentry.io/...
RATE_LIMIT_DEFAULT=50/minute
LOG_LEVEL=WARNING
```

---

## Staging Configuration

```bash
docker compose -f docker-compose.staging.yml up -d
```

The staging compose file is a stripped-down variant optimized for pre-production validation. Compared to the full development stack:

| Feature | Development | Staging |
|---|---|---|
| Source volume mounts | ✅ (hot-reload) | ❌ (pre-built image) |
| Grafana | ✅ | ❌ |
| Prometheus | ✅ | ✅ (minimal retention) |
| Resource limits | None | CPU/memory constrained |
| Environment | `development` | `staging` |
| Log level | `INFO` | `WARNING` |

This is useful for validating deployment procedures, testing database migrations, and catching issues that only appear in container environments.

---

## Kubernetes Deployment

Kubernetes manifests live in `monitoring/k8s/`. They include Deployments, Services, ConfigMaps, Secrets, and optional HorizontalPodAutoscalers for the gateway, worker, and scheduler components.

### Apply All Manifests

```bash
# Apply all manifests
kubectl apply -f monitoring/k8s/

# Check status
kubectl get pods -l app=engram
kubectl logs -f deployment/engram-gateway
```

### Architecture

The Kubernetes deployment separates concerns into distinct workloads:

| Component | Replicas | Purpose |
|---|---|---|
| `engram-gateway` | 2+ (HPA) | FastAPI API server — handles all HTTP traffic |
| `engram-worker` | 1+ | Background task worker — processes queued tasks |
| `engram-scheduler` | 1 | Workflow scheduler — triggers scheduled workflows |
| `engram-listener` | 1 | Event listener — processes Redis Stream events |

PostgreSQL and Redis should be provisioned as managed services (RDS, ElastiCache, Cloud SQL, Memorystore) in production rather than running as pods. The manifests include environment variable references to external service endpoints.

### Secrets

```bash
# Create secrets from .env file
kubectl create secret generic engram-secrets \
  --from-literal=POSTGRES_PASSWORD=<password> \
  --from-literal=AUTH_JWT_SECRET=<secret> \
  --from-literal=ANTHROPIC_API_KEY=<key> \
  --from-literal=PROVIDER_CREDENTIALS_ENCRYPTION_KEY=<fernet-key>
```

### Health Checks

The gateway exposes health check endpoints that Kubernetes uses for liveness and readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: engram-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: engram-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Monitoring Stack

Engram exposes Prometheus metrics at `/metrics` via `prometheus-fastapi-instrumentator`. The included `prometheus.yml` and Grafana provisioning files give you dashboards for:

- **Request metrics** — Rate, latency (p50/p95/p99), and error rate per endpoint
- **Tool routing** — Backend selection distribution, routing confidence scores, cache hit rates
- **Self-healing** — Drift detection frequency, auto-repair success rate, manual review queue depth
- **Circuit breaker** — Trip count, cooldown events, per-destination failure tracking
- **Task queue** — Queue depth, processing latency, lease expiration, retry count
- **Swarm Memory** — Fact count, query latency, conflict resolution frequency
- **Event stream** — Redis Streams lag, consumer group health, event processing rate

### Access Grafana

```bash
open http://localhost:3001   # Default credentials: admin / admin
```

Pre-built dashboards are auto-provisioned from `monitoring/grafana/dashboards/`. No manual configuration needed — just log in and the dashboards are ready.

### Prometheus Configuration

The included `monitoring/prometheus.yml` targets the Engram gateway:

```yaml
scrape_configs:
  - job_name: 'engram'
    scrape_interval: 15s
    static_configs:
      - targets: ['app:8000']
```

### Alerting

Configure Grafana alerts for critical conditions:

| Alert | Condition | Action |
|---|---|---|
| High error rate | > 5% 5xx responses in 5 minutes | Page on-call |
| Circuit breaker tripped | Any destination circuit opens | Notify team |
| Task queue backup | Queue depth > 100 for 10 minutes | Scale workers |
| Drift detection spike | > 10 drifts detected in 1 hour | Review tool registrations |

---

## Persistent State

| Event | Database | Redis | Tool Registry | Host Config |
|---|---|---|---|---|
| `docker compose restart` | ✅ Persists (volume) | ✅ Persists (in-memory) | ✅ Persists | ✅ Persists |
| `docker compose down` | ✅ Persists (named volume) | ❌ Lost | ✅ Persists | ✅ Persists |
| `docker compose down -v` | ❌ **Lost** | ❌ Lost | ❌ Lost | ✅ Preserved |
| Container image update | ✅ Persists | Depends | ✅ Persists | ✅ Persists |

> **Important:** The `postgres_data` named volume preserves your database across `docker compose down`. To truly reset everything, add `-v` to remove volumes. The `~/.engram/` directory on the host is never affected by Docker operations.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| App can't connect to database | Docker internal DNS not ready | Ensure `db` service is healthy: `docker compose ps`. Check `depends_on` ordering. |
| Redis connection refused | Redis hasn't started yet | Check `depends_on` ordering, or restart: `docker compose restart redis` |
| Port already in use | Another service on 8000/5432/6379 | Change port mappings in `docker-compose.yml` |
| Grafana shows no data | Prometheus not scraping | Check `monitoring/prometheus.yml` targets match service names |
| Slow startup on first run | Pulling images, installing deps | Subsequent starts are fast (cached layers). First pull is ~2GB. |
| Database migration errors | Schema out of sync | Run `docker compose exec app alembic upgrade head` |
| `asyncpg` connection errors | SSL mode incompatibility | Engram auto-strips `sslmode` for asyncpg. Check `DATABASE_URL` format. |

---

## What's Next

- **[Configuration](./07-configuration.md)** — Customize every setting for your deployment
- **[EAT Identity & Security](./12-eat-identity-security.md)** — Harden authentication for production
- **[Observability & Tracing](./14-observability-tracing.md)** — Set up monitoring and alerting
- **[Updating & Uninstalling](./04-updating-uninstalling.md)** — Keep your deployment current
