from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional
import structlog
import httpx

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PollingListener:
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task] = {}

    async def start_polling(
        self,
        *,
        poll_id: str,
        url: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        interval_seconds: Optional[float] = None,
        on_event=None,
    ) -> None:
        if poll_id in self._tasks:
            return
        interval = interval_seconds or settings.EVENT_POLL_INTERVAL_SECONDS
        self._tasks[poll_id] = asyncio.create_task(
            self._poll_loop(poll_id, url, method, params or {}, interval, on_event)
        )

    async def stop_all(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
        self._tasks.clear()

    def get_active_polls(self) -> dict[str, Any]:
        return {
            poll_id: {
                "poll_id": poll_id,
                "status": "running" if not task.done() else "stopped",
            }
            for poll_id, task in self._tasks.items()
        }

    async def _poll_loop(
        self,
        poll_id: str,
        url: str,
        method: str,
        params: Dict[str, Any],
        interval: float,
        on_event,
    ) -> None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                try:
                    if method.upper() == "POST":
                        response = await client.post(url, json=params)
                    else:
                        response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    if on_event:
                        await on_event(data)
                except Exception as exc:
                    logger.warning("Polling failed", poll_id=poll_id, error=str(exc))
                await asyncio.sleep(interval)
