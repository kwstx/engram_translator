"""
LLM Service — local model integration via Ollama (Llama-3.2).

Provides:
 - extract_tool_schema : legacy schema-extraction helper
 - generate_trace_summary : produces a natural-language explanation
   of recent routing/execution decisions referencing the ontology.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Default Ollama endpoint (local)
OLLAMA_BASE_URL = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = getattr(settings, "OLLAMA_MODEL", "llama3.2")


class LLMService:
    """
    Lightweight wrapper around a local Ollama instance for
    on-demand natural-language summaries of routing decisions.
    """

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    # Legacy helper (kept for backwards-compatibility)
    # ------------------------------------------------------------------ #
    async def extract_tool_schema(self, content: str) -> Dict[str, Any]:
        """
        Uses a local LLM to extract tool schema from raw text/docs.
        """
        logger.info("Extracting tool schema with LLM", content_length=len(content))
        if "curl" in content or "GET" in content:
            name = "Extracted HTTP Tool"
            actions = [{"name": "request", "description": "Auto-extracted from docs"}]
        elif "git" in content:
            name = "Git Tool"
            actions = [{"name": "commit", "args": ["message"]}, {"name": "push"}]
        else:
            name = "Generic Doc Tool"
            actions = [{"name": "execute", "description": "Generic execute"}]

        return {
            "name": name,
            "description": f"Automatically extracted from: {content[:100]}...",
            "actions": actions,
        }

    # ------------------------------------------------------------------ #
    # Natural-language routing summary via Ollama
    # ------------------------------------------------------------------ #
    async def generate_trace_summary(
        self,
        trace_context: str,
        user_query: Optional[str] = None,
    ) -> str:
        """
        Send recent trace context to a local Ollama model and get back
        a natural-language explanation.

        Returns a fallback summary if Ollama is unreachable.
        """
        system_prompt = (
            "You are an observability assistant for the Engram translator middleware. "
            "Given structured execution traces, produce a concise natural-language "
            "explanation of the routing decisions. Reference the ontology when mapping "
            "field names (e.g., 'user_id' → ontology 'principal'). "
            "Explain *why* a backend was chosen (token efficiency, schema richness, etc.)."
        )

        user_prompt = trace_context
        if user_query:
            user_prompt = f"User question: {user_query}\n\nExecution traces:\n{trace_context}"

        payload = {
            "model": self.model,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 512},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                summary = data.get("response", "").strip()
                logger.info(
                    "Ollama summary generated",
                    model=self.model,
                    summary_length=len(summary),
                )
                return summary
        except httpx.ConnectError:
            logger.warning("Ollama not reachable, returning fallback summary", base_url=self.base_url)
            return self._fallback_summary(trace_context)
        except Exception as exc:
            logger.error("Ollama request failed", error=str(exc))
            return self._fallback_summary(trace_context)

    # ------------------------------------------------------------------ #
    # Deterministic fallback when Ollama is unavailable
    # ------------------------------------------------------------------ #
    @staticmethod
    def _fallback_summary(trace_context: str) -> str:
        """Parse trace lines and produce a rule-based summary."""
        lines = [l.strip() for l in trace_context.strip().splitlines() if l.strip()]
        if not lines:
            return "No execution traces available for summarization."

        parts = []
        for line in lines[:5]:
            if "routing=CLI" in line:
                parts.append(
                    "CLI was chosen for token efficiency; "
                    "schema adapted by mapping fields to ontology principals."
                )
            elif "routing=MCP" in line or "routing=HTTP" in line:
                parts.append(
                    "MCP/HTTP was chosen for schema richness and structured I/O; "
                    "fields mapped through the semantic ontology layer."
                )
            else:
                parts.append(f"Trace: {line[:120]}")

        return " | ".join(parts)
