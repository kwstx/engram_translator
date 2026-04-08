# Universal Onboarding

Engram's universal onboarding system turns any API, CLI tool, or freeform documentation into a dual MCP+CLI tool definition — complete with semantic ontology alignment, field mapping, and immediate agent discoverability. This is the primary mechanism for expanding what your agents can do.

---

## How Universal Onboarding Works

The onboarding pipeline follows a consistent flow regardless of source type:

```
Source Input → Schema Parsing → Ontology Alignment → Dual MCP+CLI Generation → Registry Storage → Agent Discoverability
```

1. **Source Input** — The user provides a URL, file path, shell command, documentation text, or interactive wizard answers
2. **Schema Parsing** — The system extracts endpoints, parameters, response types, and metadata from the source
3. **Ontology Alignment** — Fields are mapped through `protocols.owl` to establish semantic equivalences across protocols
4. **Dual MCP+CLI Generation** — Both a structured MCP tool definition and a CLI wrapper are generated from a single source
5. **Registry Storage** — The tool is stored in the registry via `POST /api/v1/registry/ingest/*` or `POST /api/v1/registry/manual`
6. **Agent Discoverability** — The tool is immediately available to all connected agents for routing and execution

---

## OpenAPI Spec Ingestion

The most common onboarding path. Supports both Swagger 2.0 and OpenAPI 3.0+ specs.

```bash
# From URL
engram register openapi https://petstore.swagger.io/v2/swagger.json

# From local file
engram register openapi ./specs/my-api.yaml
```

### What Happens

1. **Validation** — The spec is fetched (URL) or read (file) and validated for structural correctness
2. **Endpoint Extraction** — Each path/method combination becomes a tool action. Parameters are classified as path, query, header, or body.
3. **Response Schema Inference** — Response schemas define the tool's output structure, used for downstream field mapping
4. **Semantic Tag Detection** — The system infers semantic tags from endpoint names, descriptions, and parameter types (e.g., a `/messages` endpoint gets tagged as "Messaging")
5. **Dual Schema Generation** — Both MCP and CLI representations are created simultaneously

### Example: Registering a Weather API

```bash
engram register openapi https://api.weather.com/v1/openapi.json
```

```
 ⠋ Validating remote OpenAPI spec...
 ⠋ Generating dual MCP/CLI schemas...
 ⠋ Refining ontology mappings...
ℹ Info: 3 schema mismatches resolved via ontology alignment

╭──── [*] Registration Summary ──────────────────────╮
│ Successfully registered: Weather API                │
│ ID: 8b4c3d2e-...                                   │
│ Test Command: engram run --tool Weather API --inspect│
╰────────────────────────────────────────────────────╯
```

---

## Partial Documentation Ingestion

When you don't have a formal spec but have documentation text, API descriptions, or even README fragments:

```bash
engram register openapi "The weather API has a GET /current endpoint that takes a city parameter as a query string and returns temperature in Celsius" --partial
```

The `--partial` flag activates LLM-powered schema extraction:

1. The documentation text is sent to `POST /api/v1/registry/ingest/docs`
2. The backend uses the configured LLM provider to parse the text into a structured tool definition
3. Confidence scores are assigned to each extracted element (endpoint path, parameters, response type)
4. Low-confidence extractions are flagged for manual review in the registration summary

This is particularly useful for:
- Internal APIs with informal documentation
- Third-party APIs that don't publish OpenAPI specs
- Rapid prototyping where you want to register a tool from a description

---

## CLI Command Ingestion

Register any shell command as a semantically-wrapped tool:

```bash
engram register command docker
engram register command kubectl
engram register command git
engram register command ffmpeg
```

### What Happens

1. **Shell Probing** — The system checks that the command exists and is executable
2. **Help Text Parsing** — Runs `<command> --help` and parses the output to discover subcommands, flags, and argument types
3. **Subcommand Discovery** — For complex CLI tools (e.g., `docker`, `kubectl`), recursively discovers subcommands
4. **Argument Inference** — Maps CLI flags to typed parameters (string, integer, boolean, array)
5. **Semantic Wrapper Synthesis** — Generates both an MCP tool definition and a CLI execution wrapper

The resulting tool can be executed by agents through either backend:
- **MCP backend** — Structured JSON invocation with parameter validation
- **CLI backend** — Direct shell execution with argument assembly

---

## Manual Interactive Registration

For full control over every field, use the interactive wizard:

```bash
engram register tool
```

The wizard walks you through:

```
Engram Manual Tool Registration
This interactive session will guide you through registering a tool without an OpenAPI spec.

Tool Name: Weather Checker
Description: Get current weather for a city
Base URL (e.g., https://api.weather.com): https://api.weather.com
Path (e.g., /v1/current): /v1/current
HTTP Method [GET/POST/PUT/DELETE] (GET): GET

Define Parameters (Press Enter on 'Parameter Name' to finish)
Parameter Name (leave blank to finish): city
Parameter Type [string/integer/boolean/number/array/object] (string): string
Parameter Description (Description for city): The city name to check weather for
Is required? [yes/no] (yes): yes

Parameter Name (leave blank to finish):

Prepared tool configuration for 'Weather Checker'
Endpoint: GET https://api.weather.com/v1/current
Parameters (1): city
```

After confirmation, the tool is registered via `POST /api/v1/registry/manual` with a synthetic OpenAPI schema generated from your inputs.

---

## Dual MCP+CLI Schema Generation

Every registered tool gets both representations automatically:

| Aspect | MCP Schema | CLI Wrapper |
|---|---|---|
| **Invocation** | Structured JSON `{"name": "tool", "arguments": {...}}` | Shell command with flags |
| **Validation** | Pydantic model with type checking | Argument parsing with type coercion |
| **Output** | JSON response | Formatted text or JSON |
| **Best for** | Structured reliability, type safety | Speed, token efficiency, scripting |

This duality is what enables the routing engine to choose the optimal backend per task. The same tool can be executed via MCP for reliability-critical workflows or via CLI for speed-sensitive tasks.

---

## Ontology Alignment During Registration

When a tool is registered, its fields are mapped through the OWL ontology (`protocols.owl`):

1. **Field Flattening** — Nested JSON structures are flattened to `dot.notation` paths
2. **Semantic Equivalence Detection** — The `SemanticMapper` looks up each field in the ontology to find equivalent concepts across protocols
3. **Cross-Protocol Normalization** — Fields like `city`, `location`, `place` are recognized as semantically equivalent through ontology concepts
4. **Initial Healing Baseline** — The established mappings become the baseline for future drift detection

This is why Engram can automatically translate payloads between protocols — the ontology provides a shared vocabulary that bridges different naming conventions.

---

## Pre-Optimized Popular Apps

Engram includes a catalog of pre-optimized tool definitions for popular services:

```bash
engram tools list --popular
```

The catalog includes warm-started definitions with:
- Validated schemas tested against live APIs
- Pre-computed semantic tags and ontology mappings
- High-confidence routing data (seeded at 99% success rate)
- Optimized CLI wrappers with efficient argument assembly

> **Note:** Pre-optimized tools appear with a `>` marker in the tools list, while your custom-registered tools show `*`. Both are fully functional — pre-optimized tools just have a head start on the learning curve.

---

## Adapter System

For deep integrations beyond simple API wrapping, Engram supports custom adapters:

```python
# adapters/base.py pattern
class BaseAdapter:
    async def connect(self, credentials: Dict) -> bool: ...
    async def execute(self, action: str, params: Dict) -> Dict: ...
    async def health_check(self) -> bool: ...
```

Built-in adapters include:
- **Mirofish** — Multi-agent orchestration connector
- **OpenClaw** — AI tool marketplace integration
- **Claude/Anthropic** — Direct LLM access
- **Perplexity** — Search-augmented generation
- **Slack** — Messaging and channel management

To add a new adapter, implement the `BaseAdapter` interface and register it in the connector registry. See the [Contributing](./19-contributing.md) guide for step-by-step instructions.

---

## What's Next

- **[Self-Healing Engine](./09-self-healing-engine.md)** — How registered tools stay working as APIs change
- **[Hybrid Routing](./10-hybrid-routing.md)** — How the router chooses between MCP and CLI backends
- **[CLI Reference](./06-cli-reference.md)** — Detailed command reference for all registration commands
