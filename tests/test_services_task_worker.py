import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.task_worker import TaskWorker
from app.db.models import Task, TaskStatus

@pytest.mark.asyncio
class TestTaskWorker:
    @patch("app.services.task_worker.sessionmaker")
    @patch("app.services.task_worker.lease_task")
    async def test_run_loop_iteration(self, mock_lease, mock_sessionmaker):
        mock_session = AsyncMock()
        mock_sessionmaker.return_value.return_value.__aenter__.return_value = mock_session
        
        task = Task(id=1, source_message={"x": 1}, source_protocol="A2A", target_protocol="MCP")
        mock_lease.side_effect = [task, None, None, None]
        
        worker = TaskWorker(poll_interval_seconds=0.1)
        
        # Mock _process_task to avoid deep logic in this test
        with patch.object(worker, "_process_task", new_callable=AsyncMock) as mock_process:
            loop_task = asyncio.create_task(worker._run_loop())
            await asyncio.sleep(0.15)
            loop_task.cancel()
            
            assert mock_lease.called
            mock_process.assert_called_with(mock_session, task)

    async def test_process_task_success(self):
        worker = TaskWorker()
        session = AsyncMock()
        task = Task(id=1, source_message={"payload": {"v": 1}}, source_protocol="A2A", target_protocol="MCP", target_agent_id="agent-1")
        
        # Mock orchestrator and translator
        worker._orchestrator = MagicMock()
        worker._orchestrator.handoff.return_value.translated_message = {"data_bundle": {"v": 1}}
        worker._orchestrator.translator.refresh_delta_mappings = AsyncMock()
        
        await worker._process_task(session, task)
        
        assert task.status == TaskStatus.COMPLETED
        assert session.add.called
        assert session.commit.called

    async def test_process_task_failure_retry(self):
        worker = TaskWorker()
        session = AsyncMock()
        task = Task(id=1, attempts=1, max_attempts=3, source_message={}, source_protocol="A2A", target_protocol="MCP")
        
        worker._orchestrator = MagicMock()
        worker._orchestrator.handoff.side_effect = Exception("error")
        worker._orchestrator.translator.refresh_delta_mappings = AsyncMock()
        
        await worker._process_task(session, task)
        
        assert task.status == TaskStatus.PENDING
        assert task.last_error == "error"
        assert session.commit.called

    async def test_process_task_failure_dead_letter(self):
        worker = TaskWorker()
        session = AsyncMock()
        task = Task(id=1, attempts=3, max_attempts=3, source_message={}, source_protocol="A2A", target_protocol="MCP", target_agent_id="agent-1")
        
        worker._orchestrator = MagicMock()
        worker._orchestrator.handoff.side_effect = Exception("final error")
        worker._orchestrator.translator.refresh_delta_mappings = AsyncMock()
        
        await worker._process_task(session, task)
        
        assert task.status == TaskStatus.DEAD_LETTER
        assert task.last_error == "final error"
        assert session.add.called # AgentMessage for dead letter
        assert session.commit.called
