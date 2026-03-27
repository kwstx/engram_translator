import httpx
import structlog
from typing import Any, Dict, Optional
from .base import BaseConnector
from app.core.config import settings

logger = structlog.get_logger(__name__)

class MiroFishConnector(BaseConnector):
    """
    Connector for MiroFish Swarm.
    Refactored from app.services.mirofish_router into the unified Connector Architecture.
    Translates Engram's unified MCP task format into MiroFish's simulation format.
    """

    def __init__(self, base_url: Optional[str] = None):
        super().__init__(name="MIROFISH")
        self.base_url = (base_url or settings.MIROFISH_BASE_URL).rstrip("/")

    def translate_to_tool(self, engram_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP -> MiroFish (simulation/start).
        """
        import json
        
        # Prefer an explicit seed_text field; fallback to serialization
        seed_text = engram_task.get("seed_text", json.dumps(engram_task, default=str))
        
        # MiroFish expects certain metadata fields to override defaults
        # We can extract those if they provide them in the MCP payload or we can just use defaults
        # For simplicity, we'll try to get them from a 'mirofish_config' or use settings
        config = engram_task.get("mirofish_config", {})
        
        request_body = {
            "seedText": seed_text,
            "numAgents": config.get("numAgents", settings.MIROFISH_DEFAULT_NUM_AGENTS),
            "swarmId": config.get("swarmId", settings.MIROFISH_DEFAULT_SWARM_ID)
        }
        
        if "godsEyeVariables" in config:
            request_body["godsEyeVariables"] = config["godsEyeVariables"]
            
        return request_body

    def translate_from_tool(self, tool_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        MiroFish Response -> Engram Unified Format.
        """
        return {
            "status": "success",
            "protocol": "MCP",
            "payload": tool_response,
            "metadata": {
                "tool": "mirofish",
                "swarm_id": tool_response.get("swarm_id", "")
            }
        }

    async def call_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs the actual API call to the MiroFish simulation engine.
        """
        endpoint = f"{self.base_url}/api/simulation/start"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(endpoint, json=tool_request)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning("MiroFishConnector: request failed, returning error response", error=str(e))
                return {
                    "status": "error",
                    "error": "mirofish_request_failed",
                    "detail": str(e),
                    "swarm_id": tool_request.get("swarmId", "n/a"),
                    "endpoint": endpoint
                }
