# Contributing

This guide helps you get set up for contributing to Engram — from development environment to code standards to submitting your first pull request.

---

## Development Environment Setup

### 1. Fork and Clone

```bash
git clone https://github.com/<your-username>/engram_translator.git
cd engram_translator
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# or: .\venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Includes test + linting tools
```

### 4. Set Up Pre-Commit Hooks

```bash
pre-commit install
```

### 5. Initialize Configuration

```bash
mkdir -p ~/.engram
python -m app.cli init
```

### 6. Start the Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Verify

```bash
curl http://localhost:8000/health
python -m app.cli info
```

---

## Project Structure

```
engram_translator/
├── app/                          # Core application
│   ├── api/v1/                   # API routers
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── discovery.py         # Agent/tool discovery
│   │   ├── endpoints.py         # General API endpoints
│   │   ├── events.py            # Event listeners and sync
│   │   ├── evolution.py         # Self-evolving tools
│   │   ├── federation.py        # Protocol translation
│   │   ├── orchestration.py     # Task orchestration
│   │   ├── reconciliation.py    # Self-healing
│   │   ├── registry.py          # Tool registration
│   │   ├── routing.py           # Routing tests/stats
│   │   └── tracing.py           # Execution traces
│   ├── cli.py                   # CLI entrypoint (Typer + Rich)
│   ├── core/
│   │   ├── config.py            # Settings model (Pydantic)
│   │   ├── security.py          # JWT validation, EAT verification
│   │   └── tui_bridge.py        # TUI event bridge
│   ├── db/
│   │   └── session.py           # Database engine and session
│   ├── main.py                  # FastAPI application
│   ├── models/                  # SQLModel/Pydantic models
│   ├── semantic/
│   │   ├── protocols.owl        # Protocol ontology
│   │   ├── security.owl         # Security ontology
│   │   ├── semantic_mapper.py   # Semantic field mapper
│   │   └── models/              # ML models (joblib)
│   └── services/
│       ├── credentials.py       # Credential encryption
│       ├── eat_identity.py      # EAT token lifecycle
│       ├── orchestrator.py      # Protocol orchestration
│       └── tool_routing.py      # Routing engine
├── bridge/
│   ├── memory.py                # Swarm Memory (SQLite + Prolog)
│   └── router.py                # Unified routing entrypoint
├── delegation/
│   └── engine.py                # Agent delegation engine
├── engram_sdk/
│   ├── auth.py                  # SDK authentication
│   ├── client.py                # SDK client
│   └── transport.py             # HTTP transport layer
├── reliability/
│   └── middleware.py            # Circuit breaker, retry, idempotency
├── tui/
│   ├── app.py                   # Textual TUI application
│   └── vault_service.py         # TUI credential vault
├── trading-templates/           # Trading integration templates
├── monitoring/
│   ├── grafana/                 # Grafana dashboards
│   ├── k8s/                     # Kubernetes manifests
│   └── prometheus.yml           # Prometheus config
├── docs/                        # Documentation (you are here)
├── tests/                       # Test suite
├── alembic/                     # Database migrations
├── docker-compose.yml           # Dev Docker Compose
├── docker-compose.staging.yml   # Staging Docker Compose
├── requirements.txt             # Python dependencies
├── setup.sh                     # Unix installer
├── engram                       # Unix self-healing entrypoint
└── engram.bat                   # Windows self-healing entrypoint
```

---

## Code Style

### Python

- **Formatter** — Black (line length: 120)
- **Linter** — Ruff (replaces flake8 + isort)
- **Type checking** — Pyright (strict mode)
- **Import order** — stdlib → third-party → local

### Key Conventions

| Convention | Standard |
|---|---|
| **Naming** | `snake_case` for functions/variables, `PascalCase` for classes |
| **Type hints** | Required on all function signatures |
| **Docstrings** | Google style for all public functions/classes |
| **Error handling** | Typed exceptions, never bare `except:` |
| **Async** | Use `async def` for all I/O operations |
| **Database** | SQLModel for models, async sessions for queries |
| **CLI** | Typer for commands, Rich for output formatting |

---

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific module
pytest tests/test_routing.py

# Verbose with output
pytest -v -s
```

### Test Structure

```
tests/
├── test_auth.py          # Authentication flows
├── test_registry.py      # Tool registration
├── test_routing.py       # Routing engine
├── test_healing.py       # Self-healing
├── test_federation.py    # Protocol translation
├── test_reliability.py   # Circuit breaker, retry
├── test_sdk.py           # SDK client
└── conftest.py           # Shared fixtures
```

### Writing Tests

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_tool_registration():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/registry/manual",
            json={
                "name": "Test Tool",
                "description": "A test tool",
                "base_url": "https://api.test.com",
                "path": "/v1/test",
                "method": "GET",
                "parameters": []
            },
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Test Tool"
```

---

## Branching Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable release branch |
| `develop` | Integration branch for features |
| `feature/<name>` | New features |
| `fix/<name>` | Bug fixes |
| `docs/<name>` | Documentation updates |

### Workflow

1. Create a feature branch from `develop`
2. Make your changes
3. Write/update tests
4. Run the full test suite
5. Open a PR against `develop`
6. Address review feedback
7. Squash and merge

---

## Pull Request Guidelines

### PR Title

Use conventional commit format:

```
feat(routing): add predictive optimization
fix(auth): handle expired refresh tokens
docs(quickstart): update installation steps
refactor(semantic): extract BidirectionalNormalizer
```

### PR Description

Include:
- **What** — Brief description of the change
- **Why** — Motivation and context
- **How** — Technical approach
- **Testing** — How you verified the change
- **Breaking changes** — If any

### Review Checklist

- [ ] Tests pass (`pytest`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`pyright`)
- [ ] Documentation updated (if user-facing)
- [ ] Database migrations included (if schema changed)
- [ ] No secrets or credentials in code

---

## Adding New Features

### Adding a New API Router

1. Create `app/api/v1/my_feature.py`
2. Define endpoints with `APIRouter(prefix="/api/v1/my-feature")`
3. Register in `app/main.py`
4. Add tests in `tests/test_my_feature.py`
5. Update documentation

### Adding a New CLI Command

1. Add command group in `app/cli.py` using `typer.Typer()`
2. Implement the command function
3. Add Rich formatting for output
4. Support `--json` output mode
5. Add to the REPL help table
6. Update CLI Reference documentation

### Adding a New Protocol Connector

1. Implement the connector interface (see existing connectors)
2. Register in the orchestrator's connector registry
3. Add ontology concepts for the new protocol's fields
4. Write federation tests
5. Update Protocol Federation documentation

### Adding a New Provider

1. Add API key setting in `app/core/config.py`
2. Create a TUI connection screen in `tui/app.py`
3. Add credential type in `app/services/credentials.py`
4. Register the provider in the backend provider list
5. Write integration tests

---

## Ontology Contributions

To extend the semantic layer:

### Adding Concepts to `protocols.owl`

```xml
<owl:Class rdf:about="#MyNewConcept">
  <rdfs:subClassOf rdf:resource="#ParentConcept"/>
  <rdfs:label>My New Concept</rdfs:label>
</owl:Class>
```

### Adding Equivalences

```xml
<owl:AnnotationProperty rdf:about="#semanticEquivalent"/>
<owl:NamedIndividual rdf:about="#field_name_a">
  <semanticEquivalent rdf:resource="#field_name_b"/>
</owl:NamedIndividual>
```

### Testing Ontology Changes

1. Load the modified ontology with `rdflib`
2. Query for the new concepts
3. Verify equivalence resolution
4. Run the full healing test suite

---

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a release branch from `develop`
4. Open PR to `main`
5. After merge, tag the release: `git tag v1.x.x`
6. Build and push Docker image
7. Deploy to staging, then production

---

## Getting Help

- **Issues** — Open a GitHub issue for bugs or feature requests
- **Discussions** — Use GitHub Discussions for questions
- **Documentation** — Check the [docs/](.) directory
- **Code** — Read the source — it's well-documented with docstrings and type hints

---

## What's Next

- **[Architecture](./17-architecture.md)** — Understand the codebase structure
- **[Installation](./02-installation.md)** — Set up your development environment
- **[CLI Reference](./06-cli-reference.md)** — Learn the command structure
