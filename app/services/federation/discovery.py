from typing import Any, Dict, List, Optional
import structlog
import uuid
from app.db.models import AgentRegistry, ToolRegistry
from app.services.federation.translator import FederationTranslator

logger = structlog.get_logger(__name__)

class FederationDiscovery:
    """
    Handles mapping of agent registries and tasks to A2A discovery cards or ACP messages.
    Uses ontology as the canonical intermediate representation.
    """

    def __init__(self, translator: Optional[FederationTranslator] = None):
        self.translator = translator or FederationTranslator()

    def to_a2a_discovery_card(self, agent: AgentRegistry) -> Dict[str, Any]:
        """
        Maps an AgentRegistry object to an A2A discovery card.
        """
        logger.info("Generating A2A discovery card", agent_id=str(agent.agent_id))
        
        # 1. Map basic fields to canonical ontology
        canonical_agent = self.translator.to_ontology({
            "agent_id": str(agent.agent_id),
            "endpoint": agent.endpoint_url,
            "supported_protocols": agent.supported_protocols,
            "capabilities": agent.capabilities,
            "semantic_tags": agent.semantic_tags
        }, "BASE") # Assuming BASE is canonical-ish
        
        # 2. Map to A2A representation
        card = {
            "id": canonical_agent.get("agent_id"),
            "service_endpoint": canonical_agent.get("endpoint"),
            "protocols": canonical_agent.get("supported_protocols", []),
            "capabilities": canonical_agent.get("capabilities", []),
            "metadata": {
                "tags": canonical_agent.get("semantic_tags", []),
                "is_active": agent.is_active,
                "compatibility": agent.success_rate
            }
        }
        
        # 3. Include tools as A2A operations (if available)
        # Assuming tools are relationships in agent registry
        if hasattr(agent, "tools"):
            card["operations"] = [
                {
                    "operation_id": t.name,
                    "description": t.description,
                    "schema": t.input_schema,
                    "protocol": "MCP" # Tools are typically MCP-ready
                }
                for t in agent.tools
            ]
            
        return card

    def to_acp_message(self, task: Dict[str, Any], task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Maps a task or intent to an ACP (Agent Control Protocol) message.
        """
        task_id = task_id or str(uuid.uuid4())
        logger.info("Generating ACP task message", task_id=task_id)
        
        # 1. Map task to canonical ontology
        canonical_task = self.translator.to_ontology(task, "BASE")
        
        # 2. Map to ACP message
        message = {
            "jsonrpc": "2.0",
            "method": "acp.task.request",
            "params": {
                "id": task_id,
                "payload": canonical_task,
                "negotiation": {
                    "strategy": "last_write_wins",
                    "priority": 1
                }
            }
        }
        
        return message

    def from_acp_message(self, acp_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps an incoming ACP message back to canonical ontology.
        """
        params = acp_message.get("params", {})
        payload = params.get("payload", {})
        
        # ACP uses JSON payloads for tasks.
        logger.info("Incoming ACP message received", task_id=params.get("id"))
        
        # We assume the payload is already canonical or we'd translate it here.
        return payload
