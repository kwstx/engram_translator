from __future__ import annotations

from typing import Any, Dict, List, Tuple
import structlog

from app.core.redis_client import get_redis_client
from app.core.config import settings

logger = structlog.get_logger(__name__)


class EventStream:
    def __init__(self) -> None:
        self.redis = get_redis_client()
        self.stream_key = settings.EVENT_STREAM_KEY
        self.group_name = settings.EVENT_STREAM_GROUP
        self.consumer_name = settings.EVENT_STREAM_CONSUMER
        self.block_ms = settings.EVENT_STREAM_BLOCK_MS
        self.batch_size = settings.EVENT_STREAM_BATCH
        self.maxlen = settings.EVENT_STREAM_MAXLEN

    def available(self) -> bool:
        return self.redis is not None

    def ensure_group(self) -> None:
        if not self.redis:
            return
        try:
            self.redis.xgroup_create(
                name=self.stream_key,
                groupname=self.group_name,
                id="0-0",
                mkstream=True,
            )
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                logger.warning("Failed to create Redis stream group", error=str(exc))

    def publish(self, payload: Dict[str, Any]) -> str | None:
        if not self.redis:
            return None
        try:
            cleaned = {k: "" if v is None else str(v) for k, v in payload.items()}
            return self.redis.xadd(
                self.stream_key,
                cleaned,
                maxlen=self.maxlen,
                approximate=True,
            )
        except Exception as exc:
            logger.warning("Failed to publish event to stream", error=str(exc))
            return None

    def read(self) -> List[Tuple[str, Dict[str, Any]]]:
        if not self.redis:
            return []
        try:
            streams = {self.stream_key: ">"}
            result = self.redis.xreadgroup(
                groupname=self.group_name,
                consumername=self.consumer_name,
                streams=streams,
                count=self.batch_size,
                block=self.block_ms,
            )
            events: List[Tuple[str, Dict[str, Any]]] = []
            for _, entries in result:
                for event_id, data in entries:
                    events.append((event_id, data))
            return events
        except Exception as exc:
            logger.warning("Failed to read from event stream", error=str(exc))
            return []

    def ack(self, event_id: str) -> None:
        if not self.redis:
            return
        try:
            self.redis.xack(self.stream_key, self.group_name, event_id)
        except Exception as exc:
            logger.warning("Failed to ack event", event_id=event_id, error=str(exc))
