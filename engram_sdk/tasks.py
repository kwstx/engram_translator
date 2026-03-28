from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from .communication import EngramTransport
from .exceptions import EngramRequestError
from .types import TaskLease, TaskSubmissionResult


class TaskClient:
    def __init__(self, transport: EngramTransport) -> None:
        self._transport = transport

    def submit_task(
        self,
        command: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TaskSubmissionResult:
        payload = {"command": command, "metadata": metadata or {}}
        response = self._transport.request_json(
            "POST",
            "/tasks/submit",
            json_body=payload,
        )
        return TaskSubmissionResult(
            task_id=str(response.get("task_id")),
            status=str(response.get("status")),
            message=response.get("message"),
        )

    def enqueue_task(
        self,
        *,
        source_message: Dict[str, Any],
        source_protocol: str,
        target_protocol: str,
        target_agent_id: str,
        max_attempts: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "source_message": source_message,
            "source_protocol": source_protocol,
            "target_protocol": target_protocol,
            "target_agent_id": target_agent_id,
        }
        if max_attempts is not None:
            payload["max_attempts"] = max_attempts
        return self._transport.request_json(
            "POST",
            "/queue/enqueue",
            json_body=payload,
        )

    def poll_messages(
        self,
        agent_id: str,
        *,
        lease_seconds: Optional[int] = None,
    ) -> Optional[TaskLease]:
        path = f"/agents/{agent_id}/messages/poll"
        if lease_seconds is not None:
            path = f"{path}?lease_seconds={lease_seconds}"

        response = self._transport.request("POST", path, auth=None)
        if response.status_code == 204:
            return None
        if response.status_code >= 400:
            raise EngramRequestError(
                f"Task poll failed ({response.status_code}): {response.text}"
            )

        payload = response.json()
        leased_until_raw = payload.get("leased_until")
        leased_until = None
        if isinstance(leased_until_raw, str):
            try:
                leased_until = datetime.fromisoformat(
                    leased_until_raw.replace("Z", "+00:00")
                )
            except Exception:
                leased_until = datetime.utcnow()
        elif isinstance(leased_until_raw, datetime):
            leased_until = leased_until_raw
        else:
            leased_until = datetime.utcnow()
        return TaskLease(
            message_id=str(payload.get("message_id")),
            task_id=str(payload.get("task_id")),
            payload=payload.get("payload") or {},
            leased_until=leased_until,
        )

    def ack_message(self, message_id: str) -> Dict[str, Any]:
        return self._transport.request_json(
            "POST",
            f"/agents/messages/{message_id}/ack",
            auth=None,
        )
