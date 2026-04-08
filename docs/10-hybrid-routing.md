# MCP + CLI Hybrid Routing

Engram's routing engine automatically selects the best execution backend — MCP for structured reliability or CLI for speed and token efficiency — for every tool invocation. The decision is based on a multi-factor weighted composite score that combines semantic similarity, historical performance, latency, cost, and user preferences.

---

## Why Hybrid Routing

The agent ecosystem has two dominant execution paradigms:

| Backend | Strengths | Weaknesses |
|---|---|---|
| **MCP** (Model Context Protocol) | Structured JSON schemas, type validation, rich error handling, standardized tool definitions | Higher token cost, more context overhead, slower for simple tasks |
| **CLI** (Command-Line Interface) | Fast execution, minimal token overhead, native shell integration, scriptable | Less structured output, fewer guarantees, harder to validate |

One size doesn't fit all. A "list files" command is faster via CLI. A "create a customer record" action is safer via MCP. Engram's router learns from execution history and makes the right choice automatically — no manual backend selection needed.

---

## Routing Algorithm

The composite score for each tool/backend candidate is:

```
score = (similarity × w_similarity) +
        (success_rate × w_success) +
        (latency_score × w_latency) +
        (token_efficiency × w_token_cost) +
        (context_score × w_context) +
        (preference × w_preference) +
        (predictive × w_predictive)
```

### Default Weights

| Factor | Weight | Variable | Purpose |
|---|---|---|---|
| Semantic Similarity | 0.55 | `ROUTING_WEIGHT_SIMILARITY` | How well the task description matches the tool |
| Success Rate | 0.20 | `ROUTING_WEIGHT_SUCCESS` | Historical success percentage |
| Latency | 0.15 | `ROUTING_WEIGHT_LATENCY` | Average execution time (lower is better) |
| Token Cost | 0.07 | `ROUTING_WEIGHT_TOKEN_COST` | Token consumption efficiency |
| Context Overhead | 0.03 | `ROUTING_WEIGHT_CONTEXT_OVERHEAD` | Prompt engineering overhead |
| User Preference | 0.10 | `ROUTING_WEIGHT_PREFERENCE` | Backend preference from config |
| Predictive | 0.15 | `ROUTING_WEIGHT_PREDICTIVE` | Forward-looking optimization |

> **Note:** Weights don't need to sum to exactly 1.0. The router normalizes the final scores. Adjust them in your `.env` or `~/.engram/config.yaml` based on your workload priorities.

---

## Sentence Embedding Matching

The semantic similarity factor uses `sentence-transformers` with the `all-MiniLM-L6-v2` model:

1. **Task description embedding** — The user's natural-language description (e.g., "send a message to the team") is embedded into a 384-dimensional vector
2. **Tool description embedding** — Each registered tool's description is pre-embedded and cached
3. **Cosine similarity** — The router computes cosine similarity between the task and each candidate tool
4. **Score normalization** — Similarity scores are mapped to [0, 1] for composite scoring

The embedding model is loaded lazily on first use and cached in memory. Change it with `ROUTING_EMBEDDING_MODEL` if you need a different model (e.g., a multilingual variant).

---

## Historical Performance Data

Every tool execution is tracked and feeds back into routing decisions:

| Metric | Description | CLI Command |
|---|---|---|
| **Success Rate** | Percentage of executions that completed without error | `engram route list` |
| **Average Latency** | Mean execution time in milliseconds | `engram route list` |
| **Average Token Cost** | Mean token consumption per execution | `engram route list` |
| **Sample Count** | Number of executions in the stats window | `engram route list` |

The rolling window (`ROUTING_STATS_WINDOW_HOURS`, default: 168 hours / 7 days) determines how far back the stats look. Older executions are excluded, so the router adapts to recent performance changes.

```bash
engram route list
```

```
      Global Tool Performance Stats
╔═════════════════╦════════════╦════════════╦═══════════╦══════════╦═════════╗
║ Tool Name       ║ Backend    ║ Avg Latency║ Success   ║ Avg Cost ║ Samples ║
╠═════════════════╬════════════╬════════════╬═══════════╬══════════╬═════════╣
║ Slack           ║ MCP        ║     245ms  ║    99.0%  ║ 12.5 tok ║     147 ║
║ Slack           ║ CLI        ║     120ms  ║    95.2%  ║  4.2 tok ║      38 ║
║ docker          ║ CLI        ║      85ms  ║    98.5%  ║  2.1 tok ║     203 ║
║ Petstore API    ║ MCP        ║     310ms  ║   100.0%  ║ 18.3 tok ║      12 ║
╚═════════════════╩════════════╩════════════╩═══════════╩══════════╩═════════╝
```

---

## Semantic Caching

Routing decisions are cached in Redis to avoid recomputing embeddings and scores for identical queries:

| Setting | Default | Purpose |
|---|---|---|
| `ROUTING_CACHE_TTL_SECONDS` | `60` | How long a routing decision is cached |

Cache invalidation happens automatically when:
- A new tool is registered
- A tool's performance stats change significantly (> 10% success rate delta)
- The tool registry is modified (description update, schema change),
- Manual cache flush via the admin API

When Redis is unavailable (local dev), routing decisions are not cached and are computed fresh each time.

---

## Parallel Confidence Threshold

When the gap between the top two candidates is below `ROUTING_PARALLEL_CONFIDENCE_THRESHOLD` (default: 0.05), the router considers running both backends simultaneously:

```python
if top_score - second_score < ROUTING_PARALLEL_CONFIDENCE_THRESHOLD:
    # Scores are too close — consider parallel execution
```

This is useful for reliability-critical workflows where you want to compare results from both backends and select the one that completes first or produces the best output.

---

## Predictive Optimization

The predictive factor looks forward based on:
- **Tool evolution trends** — If a tool's ML improvement proposals suggest it's about to get better, the predictive score increases
- **Failure pattern predictions** — If recent executions show an increasing error rate, the predictive score decreases
- **Upcoming maintenance** — If the tool's source API has scheduled maintenance windows, the score adjusts

---

## Forcing a Backend

Override the router for debugging and testing:

```bash
# Force MCP
engram route test "send notification" --force-mcp

# Force CLI
engram route test "list docker containers" --force-cli
```

When a backend is forced, the router bypasses scoring and directly selects the specified backend. All other aspects (tool selection, semantic matching) remain unchanged.

---

## Context-Aware Pruning

The `ROUTING_BUDGET_TOKEN_LIMIT` (default: 8000) controls the maximum token budget for a single routing decision:

1. All candidate tools are ranked by composite score
2. Each tool's estimated token cost is subtracted from the budget
3. Tools that would exceed the budget are pruned from the candidate set
4. The remaining top-scoring tool is selected

This prevents expensive tool chains from consuming more tokens than the user's budget allows.

---

## CLI Commands

### Test Routing

```bash
engram route test "deploy to production"
```

Shows the optimal routing decision (chosen tool, backend, confidence, latency, cost, reasoning) and an alternatives table.

### List Performance Stats

```bash
engram route list
```

Shows all tools with historical performance data aggregated across the rolling window.

---

## What's Next

- **[Self-Healing Engine](./09-self-healing-engine.md)** — How healed tools feed back into routing
- **[Observability & Tracing](./14-observability-tracing.md)** — Trace routing decisions
- **[Configuration](./07-configuration.md)** — Tune routing weights for your workload
