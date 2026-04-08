# Self-Healing Engine

Engram's self-healing engine is the core differentiator. It continuously monitors the semantic relationship between your registered tools and the actual APIs they connect to, automatically detecting and repairing schema drift, field mismatches, and output format changes — without human intervention for high-confidence fixes.

---

## What Self-Healing Means

APIs change. Fields get renamed, response formats evolve, new parameters appear, old ones get deprecated. In traditional integration middleware, these changes cause silent failures or require manual updates. Engram's self-healing engine addresses this with three mechanisms:

1. **Schema Drift Detection** — Continuous monitoring of tool execution results against the registered schema. When a field is missing, renamed, or returns an unexpected type, a "drift" is created.
2. **Automatic Field Remapping** — The OWL ontology provides semantic equivalences that allow the engine to automatically map a renamed field (e.g., `city_name` → `location`) without manual configuration.
3. **Confidence-Based Auto-Repair** — Each proposed fix is scored by confidence. High-confidence fixes (≥ 70%) are applied automatically. Low-confidence fixes are queued for manual review.

```bash
# Check current self-healing status
engram heal status

# Trigger manual repair loop
engram heal now

# Detailed view with payload excerpts
engram heal status --verbose
```

---

## OWL Ontology Layer

The semantic foundation of self-healing is built on two OWL ontologies:

### `protocols.owl` — Protocol Ontology

Located at `app/semantic/protocols.owl`, this ontology defines:

- **Protocol concepts** — MCP, CLI, A2A, ACP as formal ontology classes
- **Field semantics** — Concepts like `Location`, `Message`, `Timestamp` that exist across all protocols
- **Equivalence relations** — `city` ≡ `location` ≡ `place` — these are the same concept in different naming conventions
- **Hierarchical relationships** — `CityName` is a subclass of `Location`, which allows inheritance-based matching

### `security.owl` — Security Ontology

Located at `app/semantic/security.owl`, this ontology defines:

- **Permission concepts** — What actions are allowed on what resources
- **Semantic scopes** — Ontology-derived capabilities (e.g., `execute:tool-invocation`)
- **Access control relationships** — How scopes map to tool capabilities

Both ontologies are loaded using `rdflib` and `owlready2`, providing SPARQL query support and OWL reasoning.

---

## Semantic Mapper

The `SemanticMapper` class (`app/semantic/semantic_mapper.py`) is the engine that performs field-level translation:

### How It Works

1. **Field Flattening** — Incoming payloads are flattened from nested JSON to `dot.notation` paths. For example, `{"user": {"name": "John"}}` becomes `user.name`.
2. **Ontology Lookup** — Each field path is looked up in `protocols.owl` using `resolve_equivalent()`. This returns the semantically equivalent field name in the target protocol.
3. **Cross-Protocol Normalization** — The `BidirectionalNormalizer` handles payload translation in both directions through the ontology bridge.
4. **Dynamic Rule Synthesis** — For novel field mappings that don't exist in the ontology, the `DynamicRuleSynthesizer` uses the configured LLM to propose new mapping rules.

### Example

When an MCP tool call returns `{"city_name": "San Francisco"}` but the registered schema expects `{"location": "San Francisco"}`:

1. The execution result doesn't match the expected schema → **drift detected**
2. The `SemanticMapper` looks up `city_name` in the ontology → finds it's equivalent to `location`
3. A mapping `city_name → location` is proposed with 95% confidence
4. Since confidence ≥ 70%, the mapping is **auto-applied**
5. Future executions of this tool automatically translate the field

---

## ML Mapping Model

In addition to ontology-based matching, Engram uses a scikit-learn classifier for ML-assisted mapping:

### Training Pipeline

1. **Data Collection** — Every successful field mapping is logged as a training sample
2. **Feature Extraction** — Field names, types, nesting depth, and character n-grams are vectorized
3. **Model Training** — A scikit-learn pipeline trains on labeled mappings from `app/semantic/models/mapping_model.joblib`
4. **Minimum Samples** — Training requires at least `ML_MIN_TRAIN_SAMPLES` (default: 20) labeled examples
5. **Auto-Retraining** — After `ML_AUTO_RETRAIN_THRESHOLD` (default: 5) manual corrections, the model automatically retrains

### Confidence Scoring

Each ML-suggested mapping gets a confidence score:

| Score | Action |
|---|---|
| ≥ 85% (`ML_AUTO_APPLY_THRESHOLD`) | Auto-applied without human review |
| 70% – 84% | Auto-applied (ontology threshold) but flagged for review |
| < 70% | Queued as PENDING-REVIEW in the drift table |

---

## Reconciliation Engine

The reconciliation engine (`POST /api/v1/reconciliation/heal`) orchestrates the full healing cycle:

1. **Query drift database** — Fetches all pending drifts (failed field mappings from recent executions)
2. **Score each drift** — Combines ontology match, ML confidence, and historical correction data
3. **Apply auto-repairs** — For drifts above the confidence threshold, updates the persistent mapping table
4. **Queue manual reviews** — For low-confidence drifts, creates PENDING-REVIEW entries visible in `heal status`
5. **Update mapping versions** — Each mapping has a version number that increments on update

### CLI Commands

```bash
# View drift analysis and active mappings
engram heal status

# Same with full telemetry payload excerpts
engram heal status --verbose

# Check status and trigger repair in one command
engram heal status --fix

# Trigger manual repair immediately
engram heal now
```

### Drift Table Output

```
   Semantic Drift Analysis
╭──────────────────┬──────────────────┬──────────────────┬───────┬──────────────╮
│ Source Protocol   │ Field Drift      │ Ontology Match   │ Conf. │ Status       │
├──────────────────┼──────────────────┼──────────────────┼───────┼──────────────┤
│ MCP -> CLI       │ city_name        │ location         │ 95.0% │ AUTO-REPAIR  │
│ A2A -> MCP       │ taskDescription  │ (RESOLVE MANUAL) │ 45.0% │ PENDING-REV  │
╰──────────────────┴──────────────────┴──────────────────┴───────┴──────────────╯
```

---

## Dynamic Rule Synthesizer

For completely novel field mappings that exist neither in the ontology nor in the ML model's training data, the `DynamicRuleSynthesizer` uses the configured LLM:

1. **Context assembly** — The field name, parent object structure, surrounding fields, and recently successful mappings are bundled into a prompt
2. **LLM reasoning** — The LLM proposes a mapping with justification
3. **Confidence calibration** — The raw LLM confidence is adjusted based on structural similarity between source and target schemas
4. **Human review** — LLM-generated rules always start in PENDING-REVIEW status, regardless of confidence

This ensures that the system can handle any mapping scenario while maintaining a human-in-the-loop for unprecedented cases.

---

## Bidirectional Normalizer

The `BidirectionalNormalizer` handles payload translation in both directions:

- **Forward normalization** — Source protocol → Canonical ontology form → Target protocol
- **Reverse normalization** — Target protocol → Canonical ontology form → Source protocol

This bidirectionality is critical for:
- **Request translation** — Converting an MCP tool call into a CLI invocation
- **Response translation** — Converting a CLI output back into structured MCP format
- **Round-trip consistency** — Ensuring that `translate(translate(x))` produces semantically equivalent output

---

## How Healing Decisions Are Traced

Every healing decision is recorded in the semantic trace system:

```bash
engram trace detail .
```

The **Self-Healing Steps** section of the trace tree shows:
- Which fields triggered drift detection
- What ontology concepts were consulted
- Whether the repair was ML-assisted, ontology-based, or LLM-synthesized
- The confidence score and whether it was auto-applied or manually reviewed

This integration means you can always audit why a particular field mapping was changed and when.

---

## What's Next

- **[Hybrid Routing](./10-hybrid-routing.md)** — How healed tools influence routing decisions
- **[Observability & Tracing](./14-observability-tracing.md)** — Monitor healing activity
- **[Configuration](./07-configuration.md)** — Tune ML thresholds and ontology paths
