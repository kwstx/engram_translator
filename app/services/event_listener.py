from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone

from app.db.session import engine
from app.db.models import ToolRegistry, ToolExecutionMetadata, AgentRegistry, ExecutionType
from app.services.event_stream import EventStream
from app.services.conflict_resolver import ConflictResolver
from app.semantic.bidirectional_normalizer import BidirectionalNormalizer
from app.services.cli_watch import CLIWatchManager
from app.services.polling_listener import PollingListener

logger = structlog.get_logger(__name__)


class EventListener:
    def __init__(self) -> None:
        self.stream = EventStream()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.normalizer = BidirectionalNormalizer()
        self.cli_watch = CLIWatchManager()
        self.polling = PollingListener()

    async def start(self) -> None:
        if self._running:
            return
        if not self.stream.available():
            logger.warning("Redis not available; event listener disabled.")
            return
        self._running = True
        self.stream.ensure_group()
        await self._bootstrap_sources()
        self._task = asyncio.create_task(self._consume_loop())
        logger.info("Event listener started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
        await self.cli_watch.stop_all()
        await self.polling.stop_all()
        logger.info("Event listener stopped")

    async def _consume_loop(self) -> None:
        while self._running:
            events = await asyncio.to_thread(self.stream.read)
            if not events:
                continue
            for event_id, payload in events:
                try:
                    await self._handle_event(payload)
                except Exception as exc:
                    logger.warning("Failed to handle event", event_id=event_id, error=str(exc))
                finally:
                    await asyncio.to_thread(self.stream.ack, event_id)

    async def _handle_event(self, payload: Dict[str, Any]) -> None:
        event = self._decode_payload(payload)
        tool_id = event.get("tool_id")
        if not tool_id:
            return
        try:
            import uuid
            tool_uuid = uuid.UUID(str(tool_id))
        except Exception:
            return

        async with AsyncSession(engine) as session:
            tool = await session.get(ToolRegistry, tool_uuid)
            if not tool:
                return
            meta_result = await session.execute(
                select(ToolExecutionMetadata).where(ToolExecutionMetadata.tool_id == tool_uuid)
            )
            metadata = meta_result.scalars().first()
            source_protocol = (
                event.get("source_protocol")
                or (metadata.exec_params or {}).get("source_protocol")
                or "MCP"
            )
            ontology_result = self.normalizer.normalize_to_ontology(
                event.get("payload", {}),
                source_protocol,
                field_rules=event.get("field_rules"),
            )
            ontology_payload = ontology_result["ontology"]

            entity_key = event.get("entity_key") or f"{tool_id}:{event.get('event_type', 'event')}"
            policy = event.get("conflict_policy") or self._infer_conflict_policy(
                ontology_payload,
                metadata.exec_params if metadata else {},
            )
            source_timestamp = self._parse_timestamp(event.get("timestamp"))

            resolver = ConflictResolver(session)
            resolved_payload = await resolver.resolve(
                entity_key=entity_key,
                incoming_payload=ontology_payload,
                policy=policy,
                source_id=event.get("source_id"),
                source_timestamp=source_timestamp,
            )

            await self._dispatch(
                session,
                tool,
                metadata,
                resolved_payload,
                event,
            )

    async def _dispatch(
        self,
        session: AsyncSession,
        tool: ToolRegistry,
        metadata: Optional[ToolExecutionMetadata],
        ontology_payload: Dict[str, Any],
        event: Dict[str, Any],
    ) -> None:
        targets = await self._resolve_targets(session, event)
        if not targets:
            return

        for agent in targets:
            for protocol in agent.supported_protocols or []:
                output_payload = None
                if protocol.upper() == "MCP":
                    output_payload = self.normalizer.normalize_from_ontology(
                        ontology_payload, "MCP"
                    )
                elif protocol.upper() == "CLI":
                    if event.get("source_protocol", "").upper() == "CLI":
                        output_payload = {
                            "cli_output": event.get("payload"),
                            "ontology": ontology_payload,
                        }
                    else:
                        exec_params = metadata.exec_params if metadata else {}
                        cli_command = exec_params.get("cli_command", tool.name)
                        output_payload = self.normalizer.ontology_to_cli(
                            ontology_payload,
                            cli_command,
                            cli_args=exec_params.get("cli_args"),
                            arg_map=exec_params.get("cli_arg_map"),
                        )
                else:
                    output_payload = self.normalizer.normalize_from_ontology(
                        ontology_payload, protocol
                    )

                await self._queue_agent_message(
                    session,
                    agent_id=agent.agent_id,
                    payload={
                        "event_type": event.get("event_type", "event"),
                        "protocol": protocol,
                        "data": output_payload,
                        "ontology": ontology_payload,
                        "source": {
                            "tool_id": str(tool.id),
                            "source_protocol": event.get("source_protocol"),
                        },
                    },
                )

    async def _queue_agent_message(
        self,
        session: AsyncSession,
        agent_id: str,
        payload: Dict[str, Any],
    ) -> None:
        from app.db.models import AgentMessage, Task, TaskStatus
        import uuid

        task = Task(
            source_protocol=payload.get("source", {}).get("source_protocol") or "EVENT",
            target_protocol=payload.get("protocol") or "MCP",
            target_agent_id=uuid.UUID(str(agent_id)),
            source_message=payload,
            status=TaskStatus.COMPLETED,
        )
        session.add(task)
        await session.flush()

        message = AgentMessage(
            task_id=task.id,
            agent_id=uuid.UUID(str(agent_id)),
            payload=payload,
        )
        session.add(message)
        await session.commit()

    async def _resolve_targets(
        self, session: AsyncSession, event: Dict[str, Any]
    ) -> List[AgentRegistry]:
        target_agent_id = event.get("target_agent_id")
        if target_agent_id:
            agent = await session.get(AgentRegistry, target_agent_id)
            return [agent] if agent else []

        result = await session.execute(select(AgentRegistry).where(AgentRegistry.is_active == True))
        return list(result.scalars().all())

    async def _bootstrap_sources(self) -> None:
        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(ToolRegistry, ToolExecutionMetadata).outerjoin(
                    ToolExecutionMetadata,
                    ToolExecutionMetadata.tool_id == ToolRegistry.id,
                )
            )
            for tool, metadata in result.all():
                if not metadata or not metadata.exec_params:
                    continue
                event_sources = metadata.exec_params.get("event_sources", {})
                source_protocol = metadata.exec_params.get("source_protocol") or (
                    "CLI" if metadata.execution_type == ExecutionType.CLI else "HTTP"
                )

                for poll_source in event_sources.get("polling", []):
                    url = poll_source.get("url")
                    if not url:
                        continue
                    poll_id = f"{tool.id}:{url}"
                    await self.polling.start_polling(
                        poll_id=poll_id,
                        url=url,
                        method=poll_source.get("method", "GET"),
                        params=poll_source.get("params"),
                        interval_seconds=poll_source.get("interval_seconds"),
                        on_event=lambda data, tool_id=str(tool.id), proto=source_protocol: self._ingest_event(
                            tool_id=tool_id,
                            source_protocol=proto,
                            event_type="polling",
                            payload=data,
                        ),
                    )

                for cli_source in event_sources.get("cli_watch", []):
                    watch_id = f"{tool.id}:{cli_source.get('name', 'watch')}"
                    command = cli_source.get("command", metadata.exec_params.get("cli_command", tool.name))
                    args = cli_source.get("args", [])
                    await self.cli_watch.start_watch(
                        watch_id=watch_id,
                        command=command,
                        args=args,
                        on_event=lambda data, tool_id=str(tool.id), proto=source_protocol: self._ingest_event(
                            tool_id=tool_id,
                            source_protocol=proto,
                            event_type="cli_watch",
                            payload=data,
                        ),
                    )

    def get_active_listeners(self) -> Dict[str, Any]:
        return {
            "polling": self.polling.get_active_polls(),
            "cli_watch": self.cli_watch.get_active_watches(),
        }

    async def _ingest_event(
        self,
        *,
        tool_id: str,
        source_protocol: str,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        event = {
            "tool_id": tool_id,
            "source_protocol": source_protocol,
            "event_type": event_type,
            "payload": json.dumps(payload),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await asyncio.to_thread(self.stream.publish, event)

    def _decode_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        decoded = dict(payload)
        if isinstance(decoded.get("payload"), str):
            try:
                decoded["payload"] = json.loads(decoded["payload"])
            except Exception:
                decoded["payload"] = {"raw": decoded["payload"]}
        return decoded

    def _infer_conflict_policy(self, ontology_payload: Dict[str, Any], exec_params: Dict[str, Any]) -> str:
        policy_map = exec_params.get("conflict_policies") or {}
        for concept in ontology_payload.keys():
            if concept in policy_map:
                return policy_map[concept]
        return exec_params.get("default_conflict_policy", "last_write_wins")

    def _parse_timestamp(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None
