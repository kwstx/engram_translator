from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.core.config import settings
from app.db.models import Workflow, WorkflowSchedule
from app.db.session import engine
from app.services.workflow_runner import create_task_from_workflow

logger = structlog.get_logger(__name__)


class WorkflowScheduler:
    def __init__(
        self,
        poll_interval_seconds: float = settings.WORKFLOW_SCHEDULER_POLL_SECONDS,
        batch_size: int = settings.WORKFLOW_SCHEDULER_BATCH_SIZE,
        worker_id: Optional[str] = None,
    ):
        self.poll_interval_seconds = poll_interval_seconds
        self.batch_size = batch_size
        self.worker_id = worker_id or f"workflow-scheduler-{int(datetime.now().timestamp())}"
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if self._task is not None:
            logger.warning("WorkflowScheduler already running", worker_id=self.worker_id)
            return
        self._task = asyncio.create_task(self._run_loop())
        logger.info("WorkflowScheduler started", worker_id=self.worker_id)

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None
        logger.info("WorkflowScheduler stopped", worker_id=self.worker_id)

    async def _run_loop(self) -> None:
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        while True:
            try:
                async with async_session() as session:
                    await self._tick(session)
                await asyncio.sleep(self.poll_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("WorkflowScheduler loop error", error=str(exc), exc_info=True)
                await asyncio.sleep(self.poll_interval_seconds)

    async def _tick(self, session: AsyncSession) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(WorkflowSchedule)
            .where(WorkflowSchedule.enabled == True, WorkflowSchedule.next_run_at <= now)
            .order_by(WorkflowSchedule.next_run_at.asc())
            .limit(self.batch_size)
        )
        res = await session.execute(stmt)
        schedules = res.scalars().all()
        if not schedules:
            return

        for schedule in schedules:
            workflow_stmt = select(Workflow).where(Workflow.id == schedule.workflow_id)
            wf_res = await session.execute(workflow_stmt)
            workflow = wf_res.scalars().first()
            if not workflow:
                schedule.enabled = False
                schedule.updated_at = now
                session.add(schedule)
                await session.commit()
                logger.warning("Workflow schedule disabled (missing workflow)", schedule_id=str(schedule.id))
                continue

            if not workflow.is_active:
                schedule.next_run_at = now + timedelta(seconds=schedule.interval_seconds)
                schedule.updated_at = now
                session.add(schedule)
                await session.commit()
                continue

            if not workflow.eat:
                schedule.enabled = False
                schedule.updated_at = now
                session.add(schedule)
                await session.commit()
                logger.warning("Workflow schedule disabled (missing EAT)", workflow_id=str(workflow.id))
                continue

            schedule.last_run_at = now
            schedule.next_run_at = now + timedelta(seconds=schedule.interval_seconds)
            schedule.updated_at = now
            session.add(schedule)
            await session.commit()

            try:
                task = await create_task_from_workflow(session, workflow)
                logger.info(
                    "Scheduled workflow enqueued",
                    workflow_id=str(workflow.id),
                    task_id=str(task.id),
                )
            except Exception as exc:
                logger.error(
                    "Failed to enqueue scheduled workflow",
                    workflow_id=str(workflow.id),
                    error=str(exc),
                )
