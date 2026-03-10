from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task, TaskStatus, AgentMessage, AgentMessageStatus


async def lease_task(
    session: AsyncSession,
    lease_owner: str,
    lease_seconds: int,
) -> Optional[Task]:
    now = datetime.now(timezone.utc)
    lease_expired = and_(
        Task.status == TaskStatus.LEASED,
        Task.leased_until.is_not(None),
        Task.leased_until < now,
    )
    ready = or_(Task.status == TaskStatus.PENDING, lease_expired)

    stmt = (
        select(Task)
        .where(
            ready,
            Task.attempts < Task.max_attempts,
        )
        .order_by(Task.created_at)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    result = await session.execute(stmt)
    task = result.scalars().first()
    if not task:
        return None

    task.status = TaskStatus.LEASED
    task.attempts += 1
    task.lease_owner = lease_owner
    task.leased_until = now + timedelta(seconds=lease_seconds)
    task.updated_at = now
    await session.commit()
    await session.refresh(task)
    return task


async def lease_agent_message(
    session: AsyncSession,
    agent_id,
    lease_owner: str,
    lease_seconds: int,
) -> Optional[AgentMessage]:
    now = datetime.now(timezone.utc)
    lease_expired = and_(
        AgentMessage.status == AgentMessageStatus.LEASED,
        AgentMessage.leased_until.is_not(None),
        AgentMessage.leased_until < now,
    )
    ready = or_(AgentMessage.status == AgentMessageStatus.PENDING, lease_expired)

    stmt = (
        select(AgentMessage)
        .where(
            AgentMessage.agent_id == agent_id,
            ready,
            AgentMessage.attempts < AgentMessage.max_attempts,
        )
        .order_by(AgentMessage.created_at)
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    result = await session.execute(stmt)
    message = result.scalars().first()
    if not message:
        return None

    message.status = AgentMessageStatus.LEASED
    message.attempts += 1
    message.lease_owner = lease_owner
    message.leased_until = now + timedelta(seconds=lease_seconds)
    message.updated_at = now
    await session.commit()
    await session.refresh(message)
    return message
