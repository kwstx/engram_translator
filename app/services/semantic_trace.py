"""
Semantic Trace Service

Captures structured execution traces across all routing decisions (MCP, CLI, HTTP).
Stores traces in-memory with a bounded deque and exposes query methods for
the natural-language explanation endpoint.
"""

from __future__ import annotations

import time
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Trace Data Structures
# ---------------------------------------------------------------------------

@dataclass
class SemanticTrace:
    """One execution-path observation."""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    # Routing
    tool_name: str = ""
    action: str = ""
    routing_choice: str = ""          # CLI | MCP | HTTP
    backend_used: str = ""            # subprocess | http_client | mcp_jsonrpc

    # Scores
    similarity_score: float = 0.0
    composite_score: float = 0.0
    token_cost_est: float = 0.0
    context_overhead_est: float = 0.0

    # Reconciliation
    reconciliation_steps: List[str] = field(default_factory=list)
    pruned_tool_count: int = 0
    original_tool_count: int = 0

    # Ontological
    ontological_interpretation: str = ""
    field_mappings: Dict[str, str] = field(default_factory=dict)

    # Outcome
    success: Optional[bool] = None
    latency_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# In-Memory Trace Store
# ---------------------------------------------------------------------------

_MAX_TRACES = 2000
_trace_store: deque[SemanticTrace] = deque(maxlen=_MAX_TRACES)


def record_trace(trace: SemanticTrace) -> SemanticTrace:
    """Persist a trace to the in-memory store and emit a structured log."""
    _trace_store.append(trace)
    logger.info(
        "Semantic trace recorded",
        trace_id=trace.trace_id,
        tool_name=trace.tool_name,
        routing_choice=trace.routing_choice,
        backend_used=trace.backend_used,
        similarity_score=trace.similarity_score,
        composite_score=trace.composite_score,
        reconciliation_steps=trace.reconciliation_steps,
        ontological_interpretation=trace.ontological_interpretation,
        success=trace.success,
        latency_ms=trace.latency_ms,
    )
    return trace


def get_recent_traces(limit: int = 50) -> List[Dict[str, Any]]:
    """Return most-recent traces (newest first)."""
    items = list(_trace_store)[-limit:]
    items.reverse()
    return [t.to_dict() for t in items]


def get_trace_by_id(trace_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single trace by its ID."""
    for t in _trace_store:
        if t.trace_id == trace_id:
            return t.to_dict()
    return None


def build_summary_context(limit: int = 10) -> str:
    """
    Build a plain-text context block from recent traces suitable for
    feeding into a small local LLM to generate natural-language summaries.
    """
    traces = get_recent_traces(limit)
    if not traces:
        return "No recent execution traces available."

    lines: List[str] = []
    for i, t in enumerate(traces, 1):
        lines.append(
            f"[{i}] tool={t['tool_name']} action={t['action']} "
            f"routing={t['routing_choice']} backend={t['backend_used']} "
            f"similarity={t['similarity_score']:.3f} composite={t['composite_score']:.3f} "
            f"token_cost={t['token_cost_est']:.0f} "
            f"pruned={t['pruned_tool_count']}/{t['original_tool_count']} "
            f"ontology=\"{t['ontological_interpretation']}\" "
            f"success={t['success']} latency={t['latency_ms']:.1f}ms "
            f"field_mappings={t['field_mappings']}"
        )
    return "\n".join(lines)
