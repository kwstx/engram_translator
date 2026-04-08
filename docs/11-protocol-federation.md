# Protocol Federation

Engram bridges four agent communication protocols — MCP, CLI, A2A, and ACP — through a single semantic ontology layer. This enables seamless cross-protocol translation, multi-agent handoffs, and intent-based routing without brittle point-to-point integrations.

---

## Supported Protocols

| Protocol | Full Name | Use Case |
|---|---|---|
| **MCP** | Model Context Protocol | Structured tool invocations with JSON schemas |
| **CLI** | Command-Line Interface | Shell command execution and output parsing |
| **A2A** | Agent-to-Agent | Inter-agent communication and task delegation |
| **ACP** | Agent Communication Protocol | Standardized agent messaging framework |

Each protocol has a dedicated connector in the orchestrator that translates to and from the canonical ontology form.

---

## Translation Architecture

Every cross-protocol translation follows a three-stage pipeline:

```
Source Protocol → Canonical Bridge (OWL Ontology) → Target Protocol
```

1. **Source normalization** — The connector for the source protocol extracts semantic meaning from the payload and maps it to ontology concepts
2. **Canonical representation** — The payload exists as a protocol-neutral, ontology-backed intermediary form
3. **Target denormalization** — The connector for the target protocol translates from ontology concepts to the target's naming conventions

### Example: MCP → CLI Translation

```json
// Source (MCP)
{"name": "get_weather", "arguments": {"city": "San Francisco", "units": "imperial"}}

// Canonical Bridge (Ontology)
{"concept": "WeatherQuery", "location": "San Francisco", "measurement_system": "imperial"}

// Target (CLI)
{"command": "weather", "flags": ["--city", "San Francisco", "--units", "imperial"]}
```

### CLI Command

```bash
# Translate with demo payload
engram protocol translate --from mcp --to cli

# Translate with custom payload
engram protocol translate --from a2a --to mcp --payload '{"task": "search", "query": "AI news"}'

# Translate from file
engram protocol translate --from cli --to a2a --payload ./request.json
```

---

## The Orchestrator

The `Orchestrator` class (`app/services/orchestrator.py`) is the central coordinator for protocol operations:

### `handoff_async()`

The primary method for cross-protocol execution:

1. **Protocol detection** — Determines the source and target protocols from the request
2. **Connector dispatch** — Routes to the appropriate protocol connector
3. **Canonical translation** — Normalizes through the ontology bridge
4. **Execution** — Invokes the target protocol's execution path
5. **Proof generation** — Creates a verifiable execution proof with trace data

### Connector Registry

Each protocol has a registered connector that implements:

| Method | Purpose |
|---|---|
| `to_canonical(payload)` | Convert protocol-specific payload to ontology form |
| `from_canonical(canonical)` | Convert ontology form to protocol-specific payload |
| `execute(payload)` | Execute the translated payload |
| `health_check()` | Verify connector availability |

---

## Protocol Connectors

### MCP Connector

Translates between MCP tool call format and the canonical ontology form. Handles:
- Tool name resolution
- Argument schema validation
- Response structure mapping
- Error code translation

### CLI Connector

Translates between shell commands and the canonical ontology form. Handles:
- Command assembly from arguments
- Flag formatting (short `-f` vs long `--flag`)
- Output parsing (JSON, table, plain text)
- Exit code interpretation

### A2A Connector

Translates between Agent-to-Agent messages and the canonical ontology form. Handles:
- Task delegation format
- Agent capability discovery
- State transfer between agents
- Acknowledgment protocol

### MiroFish Connector

A specialized connector for the MiroFish multi-agent orchestration framework. Handles:
- Swarm-level task distribution
- Multi-agent consensus
- Hierarchical delegation

---

## Multi-Hop Handoffs

When a request traverses more than two protocols (e.g., A2A → MCP → CLI), each hop goes through the ontology bridge:

```
A2A → Canonical → MCP → Canonical → CLI
```

Intermediate normalization ensures:
- No information loss between hops
- Semantic consistency across all three protocols
- Complete trace lineage for debugging

---

## Session Handoff Simulation

Test multi-agent handoffs without committing real resources:

```bash
engram protocol handoff simulate --source-agent CLI-Local --target-agent Remote-MCP
```

The simulation:

1. Creates a temporary session with a unique session ID
2. Evaluates semantic readiness (can the target agent handle this protocol?)
3. Lists bridged protocols (what translations are needed)
4. Transfers state through Redis-backed persistence
5. Reports success/failure with full state dump

### Output

```
╭──── [*] Multi-Agent Federation Detail ────────────────────╮
│ 🤝 Handoff Simulation: CLI-Local -> Remote-MCP            │
│ ├── Session ID: 9a7b3c1d-...                              │
│ ├── Semantic Readiness: READY                              │
│ ├── Bridged Protocols                                      │
│ │   ├── CLI                                                │
│ │   └── MCP                                                │
│ └── Transferred State (Redis-backed)                       │
│     ├── Context                                            │
│     │   └── {"task_history": [...], "active_tools": [...]} │
│     ├── Artifacts                                          │
│     │   └── {"files": [], "data": {}}                      │
│     └── Semantic                                           │
│         └── {"ontology_version": "1.0", "mappings": {...}} │
╰───────────────────────────────────────────────────────────╯
```

---

## Intent Resolution

The `IntentResolver` class handles natural-language to structured protocol mapping:

1. **Input** — A free-form natural language request (e.g., "send a notification about the deployment")
2. **Intent classification** — The LLM classifies the intent category (messaging, deployment, data query, etc.)
3. **Protocol selection** — Based on the intent, the resolver determines the best target protocol
4. **Structured translation** — The natural language is translated into a protocol-specific structured payload

This is what enables users to submit tasks in plain English through the TUI command input, and have them automatically routed to the right protocol and tool.

---

## Execution Proofs

Every cross-protocol translation generates a verifiable execution proof containing:

| Field | Description |
|---|---|
| `trace_id` | Unique identifier for the translation |
| `source_protocol` | Origin protocol |
| `target_protocol` | Destination protocol |
| `canonical_form` | The intermediate ontology representation |
| `field_mappings` | All field translations that occurred |
| `ontology_version` | Version of the ontology used |
| `timestamp` | When the translation was performed |
| `success` | Whether the translation succeeded |

These proofs are stored in the trace system and can be queried via `engram trace detail`.

---

## Delegation Engine

The `DelegationEngine` (`delegation/engine.py`) orchestrates agent-to-agent task delegation:

### How It Works

1. **Natural-language intent parsing** — The user's task is analyzed for subtask decomposition
2. **Agent capability matching** — Available agents are evaluated for their ability to handle each subtask
3. **Subtask routing** — Each subtask is assigned to the best-fit agent
4. **Execution coordination** — Agents execute their subtasks with progress reporting to the TUI
5. **Result aggregation** — Subtask results are combined into a unified response

### Swarm Memory Integration

The delegation engine uses Swarm Memory (`bridge/memory.py`) for:

- **Fact persistence** — Subtask context is stored as semantic facts
- **Conflict resolution** — When multiple agents produce conflicting results, Prolog-based reasoning resolves the conflict
- **Ontology-backed normalization** — Cross-agent facts are normalized through the shared ontology

---

## CLI Commands

```bash
# Translate between protocols
engram protocol translate --from mcp --to cli
engram protocol translate --from a2a --to mcp --payload '{"task": "search"}'

# Simulate multi-agent handoff
engram protocol handoff simulate
engram protocol handoff simulate --source-agent CLI-Local --target-agent Remote-MCP
```

---

## What's Next

- **[EAT Identity & Security](./12-eat-identity-security.md)** — How tokens are scoped for cross-protocol access
- **[Bidirectional Sync](./13-bidirectional-sync.md)** — Event-driven sync across protocols
- **[Architecture](./17-architecture.md)** — System-level view of the orchestrator
