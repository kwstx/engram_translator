"""
Tests for context-aware pruning, semantic trace recording,
and the LLM trace summary service.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.semantic_trace import (
    SemanticTrace,
    record_trace,
    get_recent_traces,
    get_trace_by_id,
    build_summary_context,
    _trace_store,
)
from app.services.llm import LLMService


# --------------------------------------------------------------------------- #
# Semantic Trace Store
# --------------------------------------------------------------------------- #

class TestSemanticTrace:
    def setup_method(self):
        _trace_store.clear()

    def test_record_and_retrieve_trace(self):
        trace = SemanticTrace(
            tool_name="git_tool",
            action="commit",
            routing_choice="CLI",
            backend_used="subprocess",
            similarity_score=0.85,
            composite_score=0.91,
            token_cost_est=120.0,
            reconciliation_steps=["authz_enforcement", "schema_compression"],
            ontological_interpretation="CLI chosen for token efficiency; mapped 'user_id' to 'principal'",
            success=True,
            latency_ms=42.5,
        )
        result = record_trace(trace)
        assert result.trace_id == trace.trace_id

        traces = get_recent_traces(10)
        assert len(traces) == 1
        assert traces[0]["tool_name"] == "git_tool"
        assert traces[0]["routing_choice"] == "CLI"

    def test_get_trace_by_id(self):
        trace = SemanticTrace(tool_name="slack_tool", routing_choice="MCP")
        record_trace(trace)

        found = get_trace_by_id(trace.trace_id)
        assert found is not None
        assert found["tool_name"] == "slack_tool"

        not_found = get_trace_by_id("nonexistent-id")
        assert not_found is None

    def test_build_summary_context_empty(self):
        ctx = build_summary_context(10)
        assert "No recent execution traces" in ctx

    def test_build_summary_context_with_traces(self):
        record_trace(SemanticTrace(
            tool_name="jira_tool",
            action="create_issue",
            routing_choice="MCP",
            backend_used="http_client",
            similarity_score=0.72,
            composite_score=0.80,
        ))
        ctx = build_summary_context(5)
        assert "jira_tool" in ctx
        assert "routing=MCP" in ctx

    def test_traces_newest_first(self):
        record_trace(SemanticTrace(tool_name="first"))
        record_trace(SemanticTrace(tool_name="second"))
        traces = get_recent_traces(10)
        assert traces[0]["tool_name"] == "second"
        assert traces[1]["tool_name"] == "first"


# --------------------------------------------------------------------------- #
# LLM Service (fallback mode)
# --------------------------------------------------------------------------- #

class TestLLMServiceFallback:
    def test_fallback_summary_cli(self):
        ctx = "[1] tool=git action=commit routing=CLI backend=subprocess similarity=0.850 composite=0.910 token_cost=120 pruned=3/10 ontology=\"CLI chosen\" success=True latency=42.0ms field_mappings={}"
        summary = LLMService._fallback_summary(ctx)
        assert "CLI" in summary
        assert "token efficiency" in summary

    def test_fallback_summary_mcp(self):
        ctx = "[1] tool=slack action=post routing=MCP backend=http_client similarity=0.7 composite=0.8 token_cost=300 pruned=5/12 ontology=\"MCP chosen\" success=True latency=120.0ms field_mappings={}"
        summary = LLMService._fallback_summary(ctx)
        assert "MCP/HTTP" in summary
        assert "schema richness" in summary

    def test_fallback_summary_empty(self):
        summary = LLMService._fallback_summary("")
        assert "No execution traces" in summary

    @pytest.mark.asyncio
    async def test_generate_trace_summary_ollama_down(self):
        """When Ollama is unreachable, fallback summary is returned."""
        llm = LLMService(base_url="http://localhost:99999")
        ctx = "[1] tool=git action=push routing=CLI backend=subprocess similarity=0.9 composite=0.95 token_cost=80 pruned=2/8 ontology=\"CLI chosen\" success=True latency=30.0ms field_mappings={}"
        summary = await llm.generate_trace_summary(ctx)
        assert len(summary) > 0
        assert "CLI" in summary
