from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from .client import EngramSDK
    from .scope import Scope

logger = structlog.get_logger(__name__)

class RoutingEngine:
    """
    Evaluates and caches the best backend for tools using a performance-weighted graph.
    
    The RoutingEngine runs at Step setup/activation time to ensure that all routing 
    decisions are pre-calculated and deterministic before inference begins.
    """
    def __init__(self, sdk: EngramSDK):
        self.sdk = sdk
        self._cached_decisions: Dict[str, Dict[str, str]] = {}

    def setup_step(self, step_name: str, tools: List[str]) -> Dict[str, str]:
        """
        Runs the routing evaluation for all tools in a specific step.
        Queries the server-side graph to decide the best backend (CLI vs MCP) 
        and caches the results.
        """
        logger.info("routing_engine_step_setup", step=step_name, tool_count=len(tools))
        
        # We use the Scope validation mechanism as our primary evaluation engine
        # since it already wraps the /registry/scope/validate batch endpoint.
        from .scope import Scope
        temp_scope = Scope(tools=tools, step_id=f"routing_setup_{step_name}")
        temp_scope.validate(self.sdk)
        
        decisions = temp_scope.routing_decisions
        self._cached_decisions[step_name] = decisions
        
        logger.info("routing_engine_decisions_cached", step=step_name, decisions=decisions)
        return decisions

    def get_decision(self, step_name: str, tool_name: str) -> Optional[str]:
        """Retrieves a pre-calculated routing decision for a tool in a step."""
        return self._cached_decisions.get(step_name, {}).get(tool_name)
