from typing import Any, Dict, Optional, AsyncGenerator
import httpx
import structlog
import json
import asyncio
from app.services.federation.discovery import FederationDiscovery
from app.services.federation.translator import FederationTranslator

logger = structlog.get_logger(__name__)

class FederationClient:
    """
    Base client for cross-protocol federation using HTTP/SSE.
    """
    def __init__(self, endpoint_url: str, timeout: float = 30.0):
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.discovery = FederationDiscovery()
        self.translator = FederationTranslator()

    async def post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Performs a standard JSON POST."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.endpoint_url.rstrip('/')}{path}", json=payload)
            response.raise_for_status()
            return response.json()

class A2AClient(FederationClient):
    """
    Client for Agent-to-Agent (A2A) protocol.
    Includes discovery card exchange and task delegation.
    """
    async def exchange_discovery_card(self, my_agent_registry: Any) -> Dict[str, Any]:
        """Sends our discovery card to the peer and receives theirs."""
        card = self.discovery.to_a2a_discovery_card(my_agent_registry)
        logger.info("Exchanging A2A discovery card", peer=self.endpoint_url)
        return await self.post_json("/a2a/discovery", card)

    async def delegate_task(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delegates a task using A2A semantics."""
        logger.info("Delegating task via A2A", peer=self.endpoint_url)
        # Wrap task in A2A envelope if necessary
        return await self.post_json("/a2a/task", {"payload": task_payload})

class ACPClient(FederationClient):
    """
    Client for Agent Control Protocol (ACP).
    Includes negotiation patterns and task management via JSON-RPC/SSE.
    """
    async def send_acp_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sends an ACP message for task execution."""
        acp_message = self.discovery.to_acp_message(task_data)
        logger.info("Sending ACP task request", task_id=acp_message["params"]["id"])
        return await self.post_json("/acp/rpc", acp_message)

    async def stream_acp_events(self, task_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Returns an SSE stream of ACP events for a task."""
        logger.info("Subscribing to ACP SSE stream", task_id=task_id)
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", f"{self.endpoint_url.rstrip('/')}/acp/events/{task_id}") as response:
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        try:
                            yield json.loads(line[5:])
                        except json.JSONDecodeError:
                            continue
