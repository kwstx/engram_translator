"""
Tracing & Query API

Exposes endpoints for:
 - GET  /traces           — list recent semantic execution traces
 - GET  /traces/{id}      — fetch a single trace
 - POST /traces/query     — generate a natural-language summary of
                            recent routing decisions via a local LLM
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.semantic_trace import (
    build_summary_context,
    get_recent_traces,
    get_trace_by_id,
)
from app.services.llm import LLMService

router = APIRouter(prefix="/traces", tags=["Tracing"])
logger = structlog.get_logger(__name__)

_llm = LLMService()


# --------------------------------------------------------------------------- #
# Response models
# --------------------------------------------------------------------------- #

class TraceQueryRequest(BaseModel):
    question: Optional[str] = Field(
        None,
        description=(
            "Optional natural-language question about routing decisions. "
            "If omitted, a general summary is produced."
        ),
    )
    trace_limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Number of recent traces to include as context.",
    )


class TraceQueryResponse(BaseModel):
    summary: str = Field(..., description="Natural-language summary from the LLM.")
    model_used: str = Field(..., description="Model that produced the summary.")
    trace_count: int = Field(..., description="Number of traces used as context.")


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #

@router.get("", response_model=List[Dict[str, Any]])
async def list_traces(
    limit: int = Query(50, ge=1, le=500, description="Max traces to return"),
):
    """Return the most recent semantic execution traces (newest first)."""
    traces = get_recent_traces(limit)
    logger.info("Traces listed", count=len(traces))
    return traces


@router.get("/{trace_id}", response_model=Dict[str, Any])
async def read_trace(trace_id: str):
    """Fetch a single trace by its ID."""
    trace = get_trace_by_id(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


@router.post("/query", response_model=TraceQueryResponse)
async def query_traces(body: TraceQueryRequest):
    """
    Generate a natural-language summary of recent routing decisions.

    Uses a local Ollama instance (Llama-3.2 by default).  If Ollama is
    not reachable a deterministic fallback summary is returned.

    Example response:
        "CLI chosen for token efficiency; schema adapted by mapping
         'user_id' to ontology 'principal'."
    """
    context = build_summary_context(limit=body.trace_limit)
    trace_count = len(get_recent_traces(body.trace_limit))

    summary = await _llm.generate_trace_summary(
        trace_context=context,
        user_query=body.question,
    )

    logger.info(
        "Trace query completed",
        question=body.question,
        trace_count=trace_count,
        summary_length=len(summary),
    )

    return TraceQueryResponse(
        summary=summary,
        model_used=_llm.model,
        trace_count=trace_count,
    )
