import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from app.services.queue import lease_task, lease_agent_message
from app.db.models import Task, TaskStatus, AgentMessage, AgentMessageStatus

@pytest.mark.asyncio
class TestQueueService:
    async def test_lease_task_no_tasks(self):
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        session.execute.return_value = mock_result
        
        task = await lease_task(session, "worker-1", 60)
        assert task is None

    async def test_lease_task_success(self):
        session = AsyncMock()
        mock_task = Task(id=1, status=TaskStatus.PENDING, attempts=0, max_attempts=3)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_task
        session.execute.return_value = mock_result
        
        leased_task = await lease_task(session, "worker-1", 60)
        
        assert leased_task is not None
        assert leased_task.status == TaskStatus.LEASED
        assert leased_task.attempts == 1
        assert leased_task.lease_owner == "worker-1"
        assert session.commit.called
        assert session.refresh.called

    async def test_lease_agent_message_success(self):
        session = AsyncMock()
        mock_msg = AgentMessage(id=1, agent_id="agent-1", status=AgentMessageStatus.PENDING, attempts=0, max_attempts=3)
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_msg
        session.execute.return_value = mock_result
        
        leased_msg = await lease_agent_message(session, "agent-1", "worker-1", 60)
        
        assert leased_msg is not None
        assert leased_msg.status == AgentMessageStatus.LEASED
        assert leased_msg.attempts == 1
        assert session.commit.called
