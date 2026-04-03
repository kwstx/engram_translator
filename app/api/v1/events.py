import json
from typing import Optional
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid

from app.db.session import get_session
from app.db.models import ToolRegistry
from app.services.event_stream import EventStream

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/webhook/{tool_id}")
async def ingest_webhook(
    tool_id: str,
    request: Request,
    event_type: Optional[str] = Header(default="webhook", alias="X-Engram-Event"),
    db: AsyncSession = Depends(get_session),
):
    payload = await request.json()
    tool_uuid = uuid.UUID(tool_id)
    tool = await db.get(ToolRegistry, tool_uuid)
    source_protocol = "HTTP"
    if tool and tool.execution_metadata:
        source_protocol = (tool.execution_metadata.exec_params or {}).get("source_protocol") or source_protocol

    stream = EventStream()
    entity_key = None
    if isinstance(payload, dict):
        entity_key = payload.get("entity_id") or payload.get("id")

    event = {
        "tool_id": tool_id,
        "source_protocol": source_protocol,
        "event_type": event_type or "webhook",
        "payload": json.dumps(payload),
        "entity_key": entity_key,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    stream.publish(event)
    return {"status": "queued", "event_type": event_type}


@router.get("/listeners")
async def list_listeners(request: Request):
    listener = request.app.state.event_listener
    return listener.get_active_listeners()


@router.get("/recent")
async def get_recent_events(count: int = 50):
    stream = EventStream()
    return stream.get_recent_events(count=count)


@router.post("/sync")
async def add_sync_source(
    tool_id: str,
    direction: str = "both",
    source_type: str = "polling",
    params: Optional[dict] = None,
    db: AsyncSession = Depends(get_session),
    request: Request = None,
):
    from app.db.models import ToolExecutionMetadata
    from sqlmodel import select

    tool_uuid = uuid.UUID(tool_id)
    tool = await db.get(ToolRegistry, tool_uuid)
    if not tool:
        return {"error": "Tool not found"}

    result = await db.execute(
        select(ToolExecutionMetadata).where(ToolExecutionMetadata.tool_id == tool_uuid)
    )
    metadata = result.scalars().first()
    if not metadata:
        return {"error": "Metadata not found"}

    exec_params = dict(metadata.exec_params or {})
    event_sources = exec_params.get("event_sources", {})

    if source_type == "polling":
        polling = event_sources.get("polling", [])
        polling.append(params or {})
        event_sources["polling"] = polling
    elif source_type == "cli_watch":
        cli_watch = event_sources.get("cli_watch", [])
        cli_watch.append(params or {})
        event_sources["cli_watch"] = cli_watch

    exec_params["event_sources"] = event_sources
    metadata.exec_params = exec_params
    db.add(metadata)
    await db.commit()

    # Trigger restart of listeners in the background
    listener = request.app.state.event_listener
    await listener.stop()
    await listener.start()

    return {"status": "sync_added", "direction": direction}
