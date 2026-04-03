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
