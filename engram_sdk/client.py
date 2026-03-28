from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .auth import AuthClient
from .communication import EngramTransport
from .exceptions import EngramSDKError
from .tasks import TaskClient
from .tools import ToolRegistry
from .types import TaskLease, ToolDefinition

DEFAULT_BASE_URL = "http://localhost:8000/api/v1"


class EngramSDK:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        token: Optional[str] = None,
        eat: Optional[str] = None,
        timeout: float = 60.0,
        agent_id: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        supported_protocols: Optional[List[str]] = None,
        semantic_tags: Optional[List[str]] = None,
    ) -> None:
        self.transport = EngramTransport(
            base_url,
            timeout=timeout,
            token=token,
            eat=eat,
        )
        self.auth = AuthClient(self.transport)
        self.tasks = TaskClient(self.transport)
        self.tools = ToolRegistry()

        self.agent_id = agent_id
        self.endpoint_url = endpoint_url
        self.supported_protocols = supported_protocols or []
        self.semantic_tags = semantic_tags or []

    def connect(
        self,
        *,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        eat: Optional[str] = None,
        check_health: bool = True,
    ) -> bool:
        if base_url:
            self.transport.set_base_url(base_url)
        if token:
            self.transport.set_token(token)
        if eat:
            self.transport.set_eat(eat)
        if check_health:
            return self.transport.ping()
        return True

    def register_tool(self, tool: ToolDefinition) -> ToolDefinition:
        return self.tools.register(tool)

    def register_tools(self, tools: Iterable[ToolDefinition]) -> List[ToolDefinition]:
        return self.tools.register_many(tools)

    def register_agent(
        self,
        *,
        agent_id: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        supported_protocols: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        semantic_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        agent_id = agent_id or self.agent_id
        endpoint_url = endpoint_url or self.endpoint_url
        supported_protocols = supported_protocols or self.supported_protocols
        semantic_tags = semantic_tags or self.semantic_tags
        capabilities = capabilities or self.tools.capabilities()

        if not agent_id or not endpoint_url:
            raise EngramSDKError(
                "agent_id and endpoint_url are required to register an agent."
            )

        payload = {
            "agent_id": agent_id,
            "endpoint_url": endpoint_url,
            "supported_protocols": supported_protocols,
            "capabilities": capabilities,
            "semantic_tags": semantic_tags,
        }
        return self.transport.request_json("POST", "/register", json_body=payload, auth=None)

    def receive_task(
        self,
        *,
        agent_id: Optional[str] = None,
        lease_seconds: Optional[int] = None,
    ) -> Optional[TaskLease]:
        resolved_agent_id = agent_id or self.agent_id
        if not resolved_agent_id:
            raise EngramSDKError("agent_id is required to receive tasks.")
        return self.tasks.poll_messages(resolved_agent_id, lease_seconds=lease_seconds)

    def send_response(
        self,
        *,
        message_id: str,
        response_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if response_payload:
            # Placeholder for future response ingestion endpoints.
            # For now, responses are acknowledged only.
            pass
        return self.tasks.ack_message(message_id)

    def close(self) -> None:
        self.transport.close()
