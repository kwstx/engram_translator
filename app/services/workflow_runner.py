from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.models import Task, TaskStatus, Workflow
from app.messaging.multi_agent_orchestrator import MultiAgentOrchestrator


async def create_task_from_workflow(
    db: AsyncSession,
    workflow: Workflow,
    *,
    metadata_override: Optional[Dict[str, Any]] = None,
    eat_override: Optional[str] = None,
) -> Task:
    definition = workflow.definition or {}
    command = definition.get("command") or ""
    metadata = definition.get("metadata") or {}
    if metadata_override:
        metadata = {**metadata, **metadata_override}

    orchestrator = MultiAgentOrchestrator()
    plan = orchestrator._generate_plan(command)
    if not plan:
        raise ValueError("Task parser could not determine a multi-agent plan.")

    task = Task(
        user_id=workflow.user_id,
        workflow_id=workflow.id,
        source_protocol="NL",
        target_protocol="MULTI_AGENT",
        source_message={
            "command": command,
            "plan": plan,
            "metadata": metadata,
        },
        eat=eat_override or workflow.eat,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    workflow.last_run_at = datetime.now(timezone.utc)
    workflow.updated_at = workflow.last_run_at
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    return task


async def load_workflow(db: AsyncSession, workflow_id, user_id) -> Optional[Workflow]:
    stmt = select(Workflow).where(Workflow.id == workflow_id, Workflow.user_id == user_id)
    res = await db.execute(stmt)
    return res.scalars().first()
