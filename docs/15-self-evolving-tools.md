# Self-Evolving Tools

Engram's evolution pipeline uses ML to continuously improve tool definitions based on execution history. It proposes refinements to descriptions, parameter schemas, default values, and recovery strategies — then applies them through a human-reviewed (or auto-approved) workflow.

---

## How Tools Evolve

The evolution pipeline follows a continuous improvement cycle:

```
Execution History → ML Analysis → Improvement Proposals → Human Review / Auto-Apply → Tool Registry Update
```

1. **Execution History** — Every tool execution is traced, including successes, failures, parameter values, and error types
2. **ML Analysis** — The evolution engine analyzes patterns across executions to identify improvement opportunities
3. **Improvement Proposals** — Concrete changes are generated with confidence scores
4. **Review** — High-confidence proposals above `ML_AUTO_APPLY_THRESHOLD` (default: 0.85) can be auto-applied. Others require manual review.
5. **Registry Update** — Approved proposals update the tool definition in the registry with a new semantic version

---

## Improvement Types

| Type | What Changes | Example |
|---|---|---|
| **Description Refinement** | Improved tool description based on actual usage | "Send a message" → "Send a formatted Slack message to a channel or user" |
| **Parameter Schema Optimization** | Tightened action schemas based on failure analysis | Adding `enum` constraints to a `format` parameter based on observed values |
| **Default Value Tuning** | Adjusted defaults based on most common parameter values | `units` default changed from `metric` to `imperial` if 90% of calls use imperial |
| **Recovery Strategy Generation** | Pattern-based automated fallback mapping | If tool X fails with error Y, retry with tool Z instead |

---

## Evolution Pipeline

The evolution pipeline runs as a background task:

| Component | Technology | Purpose |
|---|---|---|
| **Task Queue** | Celery | Schedules periodic analysis jobs |
| **Semantic Analysis** | `transformers` + `torch` | Analyzes execution patterns for improvement signals |
| **Versioning** | Semantic Versioning (semver) | Each evolution increments the tool's version number |
| **Storage** | Database | Proposals are stored with full diff payloads |

### Trigger Conditions

Evolution analysis is triggered when:
- A tool accumulates `ML_AUTO_RETRAIN_THRESHOLD` (default: 5) corrections from manual healing
- A tool's success rate drops below a configurable threshold
- Periodic scheduled analysis (configurable via workflow scheduler)

---

## Confidence Scoring

Each improvement proposal is assigned a confidence score:

| Score | Action |
|---|---|
| ≥ 85% (`ML_AUTO_APPLY_THRESHOLD`) | Can be auto-applied (if enabled) |
| 70% – 84% | Requires manual review but flagged as "recommended" |
| < 70% | Requires manual review, flagged as "uncertain" |

The score is computed from:
- **Evidence strength** — How many executions support this change
- **Consistency** — How consistent the pattern is across different users/contexts
- **Impact** — How much the change is expected to improve success rate

---

## Review and Apply

### Status Dashboard

```bash
engram evolve status
```

```
╭──── 🔬 Self-Evolving Tools Dashboard ───────────────────────╮
│ Improvement Pipeline Status: Active                          │
│ Pending Proposals: 3                                         │
│ Total Historical Evolutions: 47                              │
│ Last ML Update: 2026-04-08 13:45:00                         │
╰──────────────────────────────────────────────────────────────╯

         [*] Pending Tool Refinements
╭──────────────────┬──────────────────┬──────────────────────────┬───────┬──────────╮
│ Tool ID / Version│ Refinement Type  │ Proposed Changes         │ Conf. │ Prop. ID │
├──────────────────┼──────────────────┼──────────────────────────┼───────┼──────────┤
│ Slack            │ Description Path │ Description Path         │ 92.0% │ 7a3f2b1c │
│ v1.0 -> v1.1     │ Refinement      │ Refinement: Improved...  │       │          │
├──────────────────┼──────────────────┼──────────────────────────┼───────┼──────────┤
│ docker           │ Parameter Schema │ Parameter Schema         │ 78.5% │ 8b4c3d2e │
│ v2.3 -> v2.4     │ Optimization    │ Optimization: Action...  │       │          │
├──────────────────┼──────────────────┼──────────────────────────┼───────┼──────────┤
│ Weather API      │ New Recovery    │ New Recovery Strategy:    │ 65.0% │ 9c5d4e3f │
│ v1.0 -> v1.1     │ Strategy        │ Pattern-based fallback.. │       │          │
╰──────────────────┴──────────────────┴──────────────────────────┴───────┴──────────╯

Use engram evolve apply <id> to authorize a specific improvement.
```

### Apply a Proposal

```bash
# Interactive apply with diff preview
engram evolve apply 7a3f2b1c
```

The command:
1. Fetches the proposal details from `GET /api/v1/evolution/status`
2. Shows a before/after diff for each changed field
3. Asks for confirmation (unless `--force` is used)
4. Applies the change via `POST /api/v1/evolution/apply/<id>`
5. Hot-redeploys the tool registry with the new version

```bash
# Skip confirmation
engram evolve apply 7a3f2b1c --force
```

---

## Recovery Strategies

When ML analysis detects a recurring failure pattern, it generates recovery strategies:

| Pattern | Strategy |
|---|---|
| Tool X fails with timeout | Retry with increased timeout, then fallback to CLI backend |
| Tool X fails with auth error | Refresh credentials and retry |
| Tool X returns malformed data | Apply field mapping correction from known-good execution |
| Tool X consistently fails after API update | Queue for re-registration with updated schema |

Recovery strategies are stored as part of the tool definition and are automatically applied by the reliability middleware during execution.

---

## Version History

Each tool maintains a version history:

- Versions follow semver: `major.minor.patch`
- **Patch** — Default value or description refinement
- **Minor** — Parameter schema change or new recovery strategy
- **Major** — Breaking schema change (rare, usually from re-registration)

Rollback to a previous version is supported through the evolution API.

---

## CLI Commands

```bash
# View dashboard
engram evolve status

# Apply a proposal (interactive)
engram evolve apply <id>

# Apply without confirmation
engram evolve apply <id> --force
```

---

## What's Next

- **[Self-Healing Engine](./09-self-healing-engine.md)** — How healing feeds into evolution
- **[Observability & Tracing](./14-observability-tracing.md)** — Monitor evolution outcomes
- **[Configuration](./07-configuration.md)** — Configure ML thresholds
