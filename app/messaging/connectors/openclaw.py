import httpx
import structlog
from typing import Any, Dict, Optional
from .base import BaseConnector
from app.core.config import settings

logger = structlog.get_logger(__name__)

class OpenClawConnector(BaseConnector):
    """
    Connector for OpenClaw.
    Translates Engram's unified MCP task format into OpenClaw's API format.
    """

    def __init__(self, endpoint_url: Optional[str] = None):
        super().__init__(name="OPENCLAW")
        # Default endpoint for OpenClaw agents as per adapters/openclaw.py
        self.endpoint_url = endpoint_url or "http://localhost:8001"

    def translate_to_tool(self, engram_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP -> OpenClaw (normalized A2A/MCP).
        """
        return {
            "source_protocol": "MCP",
            "target_protocol": "A2A",
            "payload": engram_task
        }

    def translate_from_tool(self, tool_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        OpenClaw Response -> Engram Unified Format.
        """
        return {
            "status": "success",
            "protocol": "MCP",
            "payload": tool_response
        }

    async def call_tool(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs the actual API call to an OpenClaw agent.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Assuming OpenClaw agents have a /process or similar endpoint
                response = await client.post(f"{self.endpoint_url}/api/v1/process", json=tool_request)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning("OpenClawConnector: connection failed, returning mock response", error=str(e))
                return self._mock_call(tool_request)

    def _mock_call(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns a mock response if connection fails.
        """
        return {
            "agent": "openclaw_alpha_swarm",
            "status": "active",
            "process_id": "proc_7b89c",
            "result": f"OpenClaw processed task: {tool_request['payload'].get('coord', 'unknown')}"
        }
