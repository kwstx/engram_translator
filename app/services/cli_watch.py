from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class CLIWatchManager:
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task] = {}

    async def start_watch(
        self,
        *,
        watch_id: str,
        command: str,
        args: Optional[list[str]] = None,
        on_event=None,
    ) -> None:
        if watch_id in self._tasks:
            return
        args = args or []
        self._tasks[watch_id] = asyncio.create_task(
            self._run_watch(watch_id, command, args, on_event)
        )

    async def stop_all(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
        self._tasks.clear()

    async def _run_watch(self, watch_id: str, command: str, args: list[str], on_event):
        try:
            proc = await asyncio.create_subprocess_exec(
                command,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as exc:
            logger.warning("Failed to start CLI watch", watch_id=watch_id, error=str(exc))
            return

        if not proc.stdout:
            return

        async for raw_line in proc.stdout:
            line = raw_line.decode(errors="ignore").strip()
            if not line:
                continue
            payload = self._parse_line(line)
            if on_event:
                await on_event(payload)

    def _parse_line(self, line: str) -> Dict[str, Any]:
        # Try JSON lines first
        try:
            data = json.loads(line)
            if isinstance(data, dict):
                return data
            return {"value": data}
        except Exception:
            pass

        # Fallback: key=value pairs
        if "=" in line:
            parts = line.split()
            parsed: Dict[str, Any] = {}
            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    parsed[key.strip()] = value.strip()
            if parsed:
                return parsed

        return {"message": line}
