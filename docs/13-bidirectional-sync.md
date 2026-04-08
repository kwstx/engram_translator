# Bidirectional Sync & Events

Engram's event system enables real-time bidirectional synchronization between connected tools and the bridge. Events flow through Redis Streams with semantic normalization, ontology-backed conflict resolution, and live monitoring via the CLI and TUI.

---

## Event Architecture

Events in Engram flow through a Redis Streams pipeline:

```
Tool/Agent → Event Emission → Redis Stream (engram:events) → Consumer Group → Event Handlers → Trace/TUI
```

| Component | Implementation | Purpose |
|---|---|---|
| **Stream Key** | `engram:events` | Central event stream |
| **Consumer Group** | `engram-event-workers` | Ensures exactly-once processing |
| **Consumer** | `worker-1` | Individual consumer within the group |
| **Block Timeout** | 2000ms | How long to wait for new events |
| **Batch Size** | 25 | Events processed per read |
| **Max Length** | 10,000 | Stream trimming limit |

When Redis is unavailable (local dev), the system falls back to a polling listener with configurable interval (`EVENT_POLL_INTERVAL_SECONDS`, default: 10s).

---

## Polling Listeners

HTTP endpoint polling for tools that don't support webhooks:

```bash
engram sync add <tool-id> --type polling --url https://api.example.com/changes --interval 30
```

| Setting | Type | Description |
|---|---|---|
| `--url` | `str` | URL to poll for changes |
| `--interval` | `int` | Polling interval in seconds (default: 60) |
| `--direction` | `str` | Sync direction: `both`, `to_mcp`, `from_mcp` |

Polled data is semantically normalized through the ontology before being stored or forwarded.

---

## CLI Watch

Monitor file system changes or command output in real time:

```bash
engram sync add <tool-id> --type cli_watch --command "docker ps --format json"
```

The CLI watch service:
1. Executes the specified command at regular intervals
2. Compares output against the previous execution
3. Detects structural changes (new fields, removed fields, value changes)
4. Emits events for detected changes
5. Applies semantic normalization before storage

---

## Bidirectional Sync

Tools can be synchronized in both directions:

| Direction | Data Flow | Use Case |
|---|---|---|
| `both` | Tool ↔ Bridge | Full two-way sync (default) |
| `to_mcp` | Tool → Bridge | Read-only import from external source |
| `from_mcp` | Bridge → Tool | Push changes from bridge to external tool |

Bidirectional sync ensures that changes made in either the tool or the bridge are reflected in both systems. The ontology handles field name translation between the tool's native format and the bridge's canonical format.

---

## Semantic Conflict Resolution

When events from multiple sources conflict, Engram uses a multi-layer resolution strategy:

### Prolog-Based Reasoning

The `bridge/memory.py` module uses `pyswip` (SWI-Prolog bindings) for semantic fact reasoning:

- Facts are asserted as Prolog terms: `fact(concept, subject, predicate, value, timestamp)`
- Conflict detection queries: "Are there two facts about the same subject with different values?"
- Resolution rules: Ontology-backed reasoning determines which value takes precedence

### pyDatalog Rules

For simpler conflict scenarios, `pyDatalog` provides declarative last-write-wins rules:

- Most recent timestamp wins by default
- Configurable to prefer specific sources over others
- Cross-agent facts are reconciled through the shared ontology

### Resolution Priority

1. **Ontology authority** — If the ontology defines a canonical value, it wins
2. **Recency** — More recent writes take precedence
3. **Source trust** — Configurable per-source trust levels
4. **Manual override** — User can explicitly resolve conflicts via the API

---

## Event Normalization

Events from different sources are normalized through the ontology before storage:

```
Raw Event → Field Flattening → Ontology Lookup → Canonical Form → Storage
```

This ensures that events from different tools about the same concepts are stored in a consistent format, enabling cross-tool queries and aggregation.

---

## Swarm Memory

Swarm Memory (`bridge/memory.py`) is a persistent, ontology-aware fact store:

| Layer | Technology | Purpose |
|---|---|---|
| **Persistence** | SQLite | Durable fact storage |
| **Reasoning** | SWI-Prolog (`pyswip`) | Semantic inference and conflict detection |
| **Rules** | pyDatalog | Declarative conflict resolution |
| **Normalization** | SemanticMapper | Ontology-backed concept normalization |

### Key Operations

| Method | Purpose |
|---|---|
| `store_fact(concept, data)` | Store a semantic fact with ontology alignment |
| `query_facts(concept, filters)` | Query facts with Prolog-backed reasoning |
| `resolve_conflict(facts)` | Apply conflict resolution rules |
| `get_context(agent_id)` | Retrieve all facts relevant to an agent's current task |

---

## CLI Commands

```bash
# List active listeners
engram sync list

# Add polling sync
engram sync add <tool-uuid> --type polling --url https://api.example.com/changes --interval 30

# Add CLI watch
engram sync add <tool-uuid> --type cli_watch --command "docker ps --format json"

# Live event monitoring (auto-refresh)
engram sync status
```

### Live Monitoring

`engram sync status` uses Rich's `Live` display to show a continuously updating event table:

```
        Live Event Stream
┌──────────┬──────────┬───────────┬─────────────┬──────────────┐
│ Time     │ Tool     │ Type      │ Entity Key  │ Conflict Res │
├──────────┼──────────┼───────────┼─────────────┼──────────────┤
│ 14:23:01 │ 8b4c3d2e │ update    │ user-123    │ semantic-mtch│
│ 14:22:58 │ 7a3f2b1c │ create    │ order-456   │ semantic-mtch│
│ 14:22:55 │ 8b4c3d2e │ delete    │ item-789    │ semantic-mtch│
└──────────┴──────────┴───────────┴─────────────┴──────────────┘
Monitoring live events... Press Ctrl+C to stop.
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/events/listeners` | `GET` | List active listeners and watchers |
| `/events/sync` | `POST` | Add a new sync configuration |
| `/events/recent` | `GET` | Get recent events for live monitoring |

---

## What's Next

- **[Observability & Tracing](./14-observability-tracing.md)** — Monitor event processing
- **[Architecture](./17-architecture.md)** — System-level event architecture
- **[Configuration](./07-configuration.md)** — Configure event stream settings
